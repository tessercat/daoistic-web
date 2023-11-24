""" Management utility to create unihan radical and character tables. """
import csv
import glob
from itertools import islice
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from unihan.models import UnihanCharacter, UnihanRadical
from unihan.views import get_block


K_FIELDS = {
    'kRSUnicode',
    'kTraditionalVariant',
    'kSimplifiedVariant',
    'kSemanticVariant',
    'kSpecializedSemanticVariant',
    'kDefinition',
    'kMandarin',
    'kHanyuPinyin'
}


def _add_calculated_fields(codepoint, fields, radical_data):
    """ Add calculated fields to character data. """

    # Add codepoint fields.
    cp_int = int(codepoint.rsplit('+', 1)[1], 16)
    fields['pCodepoint'] = codepoint
    fields['pCodepointChr'] = chr(cp_int)
    fields['pCodepointInt'] = cp_int

    # Add radical/sort fields.
    rs_parts = fields['kRSUnicode'].split()[0].split('.')  # First entry only.
    rad_num = rs_parts[0]
    rad_num_int = int(rs_parts[0].rstrip('\''))
    residual_strokes = int(rs_parts[1])
    fields['pAdditionalStrokesInt'] = residual_strokes
    fields['pIsRadicalSimplified'] = rs_parts[0].endswith('\'')
    fields['pRadicalCodepoint'] = radical_data[rad_num]['pCodepoint']
    fields['pRadicalNumber'] = rad_num
    fields['pRadicalNumberInt'] = rad_num_int
    fields['kDefaultSortKey'] = _get_sort_key(
        fields['pCodepointChr'],
        cp_int,
        fields['pIsRadicalSimplified'],
        rad_num_int,
        residual_strokes,
    )

    # Add pinyin field.
    pinyin = []
    if 'kMandarin' in fields:
        # The last item is TW.
        pinyin.append(fields['kMandarin'].split()[-1])
    if 'kHanyuPinyin' in fields:
        parts = fields['kHanyuPinyin'].split(':')[-1].split(',')
        for part in parts:
            if len(pinyin) == 2:
                break
            if part not in pinyin:
                pinyin.append(part)
    if pinyin:
        fields['pPinyin'] = ' '.join(pinyin)

    # Add traditional variants field.
    if 'kTraditionalVariant' in fields:
        variants = _get_variants(fields['kTraditionalVariant'])
        if cp_int in variants:
            variants.remove(cp_int)
        if variants:
            fields['pTraditionalVariants'] = ''.join(variants)

    # Add simplified variants field.
    if 'kSimplifiedVariant' in fields:
        variants = _get_variants(fields['kSimplifiedVariant'])
        if cp_int in variants:
            variants.remove(cp_int)
        if variants:
            fields['pSimplifiedVariants'] = ''.join(variants)

    # Add semantic variants field.
    variants = set()
    semantic_variant_fields = [
        'kSemanticVariant',
        'kSpecializedSemanticVariant',
    ]
    for variant_field in semantic_variant_fields:
        if variant_field in fields:
            variants.update(_get_variants(fields[variant_field]))
    if cp_int in variants:
        variants.remove(cp_int)
    if variants:
        fields['pSemanticVariants'] = ''.join(variants)


def _create_chars(char_data, radical_objs):
    """ Bulk create character objects from raw character data for
    non-radical characters. """
    count = 0
    batch_size = 50  # SQLite 999 variable limit.
    values = iter(char_data.values())
    while True:
        batch = list(islice(values, batch_size))
        if not batch:
            break
        objs = []
        for char in batch:
            objs.append(UnihanCharacter(
                codepoint=char['pCodepointInt'],
                definition=char.get('kDefinition') or '',
                pinyin=char.get('pPinyin') or '',
                radical=radical_objs[char['pRadicalCodepoint']],
                residual_strokes=char['pAdditionalStrokesInt'],
                simplified_variants=char.get('pSimplifiedVariants') or '',
                traditional_variants=char.get('pTraditionalVariants') or '',
                semantic_variants=char.get('pSemanticVariants') or '',
                sort_order=char['kDefaultSortKey'],
                utf8=char['pCodepointChr'],
            ))
        count += len(batch)
        if count % 10000 == 0:
            print('Created %d character records' % count)
        UnihanCharacter.objects.bulk_create(objs, batch_size)
    print('Created %d character records' % count)


def _create_radicals(radical_char_data, radical_data):
    """ Bulk create character and radical objects only for radicals
    and return a dict mapping codepoint string (U+XXXX) to UnihanRadical
    objects. """

    # Create UnihanCharacter objects for each radical.
    batch_size = 50  # SQLite 999 variable limit.
    values = iter(radical_char_data)
    char_objs = {}  # Indexed by codepoint string.
    while True:
        batch = list(islice(values, batch_size))
        if not batch:
            break
        objs = []
        for char in batch:
            obj = UnihanCharacter(
                codepoint=char['pCodepointInt'],
                definition=char.get('kDefinition') or '',
                pinyin=char.get('pPinyin') or '',
                residual_strokes=char['pAdditionalStrokesInt'],
                simplified_variants=char.get('pSimplifiedVariants') or '',
                traditional_variants=char.get('pTraditionalVariants') or '',
                semantic_variants=char.get('pSemanticVariants') or '',
                sort_order=char['kDefaultSortKey'],
                utf8=char['pCodepointChr'],
            )
            char_objs[char['pCodepoint']] = obj
            objs.append(obj)
        UnihanCharacter.objects.bulk_create(objs, batch_size)

    # Create UnihanRadical objects for each radical.
    values = iter(radical_data.values())
    radical_objs = {}  # Indexed by codepoint string.
    while True:
        batch = list(islice(values, batch_size))
        if not batch:
            break
        objs = []
        for rad in batch:
            obj = UnihanRadical(
                character=char_objs[rad['pCodepoint']],
                radical_number=rad['pRadicalNumberInt'],
                simplified=rad['pIsSimplified'],
                utf8=rad['pCodepointChr'],
            )
            radical_objs[rad['pCodepoint']] = obj
            objs.append(obj)
        UnihanRadical.objects.bulk_create(objs, batch_size)

    # Update radical field in char objects.
    for key, value in char_objs.items():
        UnihanCharacter.objects.filter(pk=value.codepoint).update(
            radical=radical_objs[key],
        )

    # Return dict of UnihanRadical objects.
    print('Created %d character and radical records.' % len(radical_objs))
    return radical_objs


def _get_char_data(data_file):
    """ Return a dict mapping codepoint strings to a dict of fields
    and their values. """
    data = {}
    summary = {}
    basename = os.path.basename(data_file)
    with open(data_file) as csvfile:
        rdr = csv.reader(csvfile, delimiter='\t')
        for line in rdr:
            if line and not line[0].startswith('#'):
                if line[1] in K_FIELDS:
                    if summary.get(line[1]):
                        summary[line[1]] += 1
                    else:
                        summary[line[1]] = 1
                    if not data.get(line[0]):
                        data[line[0]] = {}
                    data[line[0]].update({line[1]: line[2]})
    print(f'{basename} {summary}')
    return data


def _get_radical_data(data_file):
    """ Return a dict of dicts of radical data indexed by radical number
    string, including the \' that indicates simplified/traditional. """
    data = {}
    with open(data_file) as csvfile:
        rdr = csv.reader(csvfile, delimiter=';')
        for line in rdr:
            if line and not line[0].startswith('#') and len(line) == 3:
                rad_num = line[0].strip()
                ideograph = line[2].strip()
                codepoint = 'U+%s' % ideograph
                codepoint_int = int(ideograph, 16)
                radical = {
                    'pCodepoint': codepoint,
                    'pCodepointChr': chr(codepoint_int),
                    'pCodepointInt': codepoint_int,
                    'pIsSimplified': rad_num.endswith('\''),
                    'pRadicalNumber': rad_num,
                    'pRadicalNumberInt': int(rad_num.rstrip('\'')),
                }
                data[rad_num] = radical
    return data


def _get_sort_key(char, cp, is_simp, rad_int, res):
    """ Return integer kDefaultSortKey sort order key defined in tr38. """

    # Block.
    block = get_block(char)
    # print(char, hex(cp), block)
    if block < 0:
        raise ValueError('CJK block not found for %s' % char)

    # Radical.
    r_hex = hex(rad_int)[2:].zfill(2)

    # Strokes.
    if res < 0:
        res = 0
    st_hex = hex(res)[2:].zfill(2)

    # First Residual Stroke.
    frs_hex = '0'

    # Simplified.
    simp_hex = '0'
    if is_simp:
        simp_hex = '1'

    # Block.
    block_hex = hex(block)[2:].zfill(2)

    # Code Point.
    cp_hex = hex(cp)[2:].zfill(5)

    return int(r_hex + st_hex + frs_hex + simp_hex + block_hex + cp_hex, 16)


def _get_variants(variant_data):
    """ Return a set of Unicode chrs derived from variant data. """
    chars = set()
    for var in variant_data.split():
        var = var.split('<')[0]
        chars.add(chr(int(var.split('+', 1)[1], 16)))
    return chars


class Command(BaseCommand):
    """ A command to import unihan db data. """

    help = 'Used to import unihan db data.'
    requires_migrations_checks = True

    def handle(self, *args, **options):
        """ Import unihan data. """

        # https://www.unicode.org/Public/UCD/latest/ucd/CJKRadicals.txt
        # https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip
        data_dir = settings.BASE_DIR / 'var' / 'unihan'

        # Get radical data, a dict indexed by radical number.
        radical_data = _get_radical_data(
            os.path.join(data_dir, 'CJKRadicals.txt')
        )

        # Get character data, a dict indexed by codepoint (U+XXXX).
        char_data = {}
        for data_glob in glob.glob(os.path.join(data_dir, 'Unihan_*.txt')):
            data = _get_char_data(os.path.join(data_dir, data_glob))
            for codepoint, values in data.items():
                if char_data.get(codepoint):
                    char_data[codepoint].update(values)
                else:
                    char_data[codepoint] = values

        # Add calculated fields to character data.
        for codepoint, values in char_data.items():
            _add_calculated_fields(codepoint, values, radical_data)

        # Pop radicals from character data.
        radical_char_data = []
        for rad in radical_data.values():
            radical_char_data.append(
                char_data.pop(rad['pCodepoint'], None)
            )

        # Create radicals and characters.
        radical_objs = _create_radicals(radical_char_data, radical_data)
        _create_chars(char_data, radical_objs)
