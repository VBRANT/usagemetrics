'''Apply and assess filter sets.

David King <d.j.king@open.ac.uk> for ViBRANT <http://vbrant.eu> March 2012
'''

import csv
import re
import sys
from test_filter_sets import includes, includes_term, \
    excludes, excludes_term, strong_excludes, strong_excludes_term

def match_template(search_terms, search_field):
    '''To see if filter terms are found in the Service Provider.
       Match on term characters, so dsl will match adsl for example.'''
    for term in search_terms:
        if term in search_field:
            return term
    return False

def match_term(search_terms, search_field):
    '''To see if filter terms are found in the Service Provider.
       Match on exact term only, so dsl will not match adsl for example.'''
    for term in search_terms:
        if re.search('\\b' + term + '\\b', search_field):
            return term
    return False

def match_number(search_field):
    '''To see if a number is found in the Service Provider.
       Match on any digit anywhere in the Service Provider name.'''
    return 'number' if re.search('\d', search_field) else False

def stats(f_pos, f_neg, t_pos, t_neg):
    '''To calculate precision, recall and f-measure.
       Overloaded function I know,
       should be three separate functions but this is a hack ;-)'''

    # precision [tp/(tp+fp)]
    divisor = t_pos + f_pos
    if divisor is not 0:
        p = round((t_pos / divisor), 2)
    else:
        p = 0

    # recall [tp/(tp+fn)]
    divisor = t_pos + f_neg
    if divisor is not 0:
        r = round(t_pos / divisor, 2)
    else:
        r = 0

    # f-measure [(p*r)/(p+r)]
    divisor = p + r
    if divisor is not 0:
        f = 2 * round((p * r) / divisor, 2)
    else:
        f = 0

    return (p, r, f)

# start of script proper
print('\napply and assess started\n')

'''
# get filter name
if len(sys.argv) != 2:
    print('no name given\nscript exiting')
else:
    file_name = sys.argv[1];
'''

# ready the stats
tot_inc = tp_inc = fp_inc = tn_inc = fn_inc = 0
tot_exc = tp_exc = fp_exc = tn_exc = fn_exc = 0
tot_oth = tp_oth = fp_oth = tn_oth = fn_oth = 0

# ready the files
# set path if data not in the same directory as the script
filepath = 'Clustering/'
# core filename to expand as required below
filename = 'Gold1000B'
# and open the files
source_data = open(filepath + filename + '.csv', 'r')
filtered_data = open(filepath + filename + '-filtered.csv', 'w', newline='')
log_include = open(filepath + filename + '-include.log', 'w')
log_exclude = open(filepath + filename + '-exclude.log', 'w')
log_other = open(filepath + filename + '-other.log', 'w')

# now filter the ISPs one row at a time
reader = csv.reader(source_data)
writer = csv.writer(filtered_data)

# for each row apply type according to filter set rules
for row in reader:
    row_mark = 'o'
    matched = match_template(strong_excludes, row[0])
    if matched:
        row_mark = 'e'
    else:
        matched = match_term(strong_excludes_term, row[0])
        if matched:
            row_mark = 'e'
        else:
            matched = match_template(includes, row[0])
            if matched:
                row_mark = 'i'
            else:
                matched = match_term(includes_term, row[0])
                if matched:
                    row_mark = 'i'
                else:
                    matched = match_number(row[0])
                    if matched:
                        row_mark = 'e'
                    else:
                        matched = match_template(excludes, row[0])
                        if matched:
                            row_mark = 'e'
                        else:
                            matched = match_term(excludes_term, row[0])
                            if matched:
                                row_mark = 'e'

# mark the output
# marking matrix
# i    i    tp_inc    tn_exc    tn_oth
# i    e    fn_inc    fp_exc    tn_oth
# i    o    fn_inc    tn_exc    fp_oth
# e    i    fp_inc    fn_exc    tn_oth
# e    e    tn_inc    tp_exc    tn_oth
# e    o    tn_inc    fn_exc    fp_oth
# o    i    fp_inc    tn_exc    fn_oth
# o    e    tn_inc    fp_exc    fn_oth
# o    o    tn_inc    tn_exc    tp_oth

    row[4] = row_mark
    if row[3] == 'i':
        tot_inc += 1
        if row_mark == 'i':
            log_include.write('found {} in {}\n'.format(matched, row[0]))
            tp_inc += 1
            tn_exc += 1
            tn_oth += 1
        elif row_mark == 'e':
            log_include.write('found {} in {} ** marked as exclude **\n'.format(matched, row[0]))
            fn_inc += 1
            fp_exc += 1
            tn_oth += 1
        elif row_mark == 'o':
            log_include.write('found nothing in {} ** marked as other **\n'.format(row[0]))
            fn_inc += 1
            tn_exc += 1
            fp_oth += 1
    elif row[3] =='e':
        tot_exc += 1
        if row_mark == 'i':
            log_exclude.write('found {} in {} ** marked as include **\n'.format(matched, row[0]))
            fp_inc += 1
            fn_exc += 1
            tn_oth += 1
        elif row_mark == 'e':
            log_exclude.write('found {} in {}\n'.format(matched, row[0]))
            tn_inc += 1
            tp_exc += 1
            tn_oth += 1
        elif row_mark == 'o':
            log_exclude.write('found nothing in {} ** marked as other **\n'.format(row[0]))
            tn_inc += 1
            fn_exc += 1
            fp_oth += 1
    elif row[3] =='o':
        tot_oth += 1
        if row_mark == 'i':
            log_other.write('found {} in {} ** marked as include **\n'.format(matched, row[0]))
            fp_inc += 1
            tn_exc += 1
            fn_oth += 1
        elif row_mark == 'e':
            log_other.write('found {} in {} ** marked as exclude **\n'.format(matched, row[0]))
            tn_inc += 1
            fp_exc += 1
            fn_oth += 1
        elif row_mark == 'o':
            log_other.write('found nothing in {}\n'.format(row[0]))
            tn_inc += 1
            tn_exc += 1
            tp_oth += 1

    # write out marked output
    writer.writerow(row)

# prepare the stats
sum_inc = tp_inc + fp_inc + tn_inc + fn_inc;
sum_exc = tp_exc + fp_exc + tn_exc + fn_exc;
sum_oth = tp_oth + fp_oth + tn_oth + fn_oth;

stats_inc = stats(fp_inc, fn_inc, tp_inc, tn_inc);
stats_exc = stats(fp_exc, fn_exc, tp_exc, tn_exc);
stats_oth = stats(fp_oth, fn_oth, tp_oth, tn_oth);

# write out the stats
log_include.write('\n\n{:12s} {:6d}\n\n'.format('includes:', tot_inc))
log_include.write('{:12s} {:6d}\n'.format('false pos:', fp_inc))
log_include.write('{:12s} {:6d}\n'.format('false neg:', fn_inc))
log_include.write('{:12s} {:6d}\n'.format('true pos:', tp_inc))
log_include.write('{:12s} {:6d}\n'.format('true neg:', tn_inc))
log_include.write('{:12s} {:6d}\n\n'.format('sum:', sum_inc))
log_include.write('{:12s} {:6.2f}\n'.format('precision:', stats_inc[0]))
log_include.write('{:12s} {:6.2f}\n'.format('recall:', stats_inc[1]))
log_include.write('{:12s} {:6.2f}\n'.format('f-measure:', stats_inc[2]))

log_exclude.write('\n\n{:12s} {:6d}\n\n'.format('excludes:', tot_exc))
log_exclude.write('{:12s} {:6d}\n'.format('false pos:', fp_exc))
log_exclude.write('{:12s} {:6d}\n'.format('false neg:', fn_exc))
log_exclude.write('{:12s} {:6d}\n'.format('true pos:', tp_exc))
log_exclude.write('{:12s} {:6d}\n'.format('true neg:', tn_exc))
log_exclude.write('{:12s} {:6d}\n\n'.format('sum:', sum_exc))
log_exclude.write('{:12s} {:6.2f}\n'.format('precision:', stats_exc[0]))
log_exclude.write('{:12s} {:6.2f}\n'.format('recall:', stats_exc[1]))
log_exclude.write('{:12s} {:6.2f}\n'.format('f-measure:', stats_exc[2]))

log_other.write('\n\n{:12s} {:6d}\n\n'.format('other:', tot_oth))
log_other.write('{:12s} {:6d}\n'.format('false pos:', fp_oth))
log_other.write('{:12s} {:6d}\n'.format('false neg:', fn_oth))
log_other.write('{:12s} {:6d}\n'.format('true pos:', tp_oth))
log_other.write('{:12s} {:6d}\n'.format('true neg:', tn_oth))
log_other.write('{:12s} {:6d}\n\n'.format('sum:', sum_oth))
log_other.write('{:12s} {:6.2f}\n'.format('precision:', stats_oth[0]))
log_other.write('{:12s} {:6.2f}\n'.format('recall:', stats_oth[1]))
log_other.write('{:12s} {:6.2f}\n'.format('f-measure:', stats_oth[2]))

print('\n              include  exclude    other')
print('{:12s} {:8d} {:8d} {:8d}'.format('totals:', tot_inc, tot_exc, tot_oth))
print('{:12s} {:8d} {:8d} {:8d}'.format('false pos:', fp_inc, fp_exc, fp_oth))
print('{:12s} {:8d} {:8d} {:8d}'.format('false neg:', fn_inc, fn_exc, fn_oth))
print('{:12s} {:8d} {:8d} {:8d}'.format('true pos:', tp_inc, tp_exc, tp_oth))
print('{:12s} {:8d} {:8d} {:8d}'.format('true neg:', tn_inc, tn_exc, tn_oth))
print('{:12s} {:8d} {:8d} {:8d}\n'.format('sum:', sum_inc, sum_exc, sum_oth))
print('{:12s} {:8.2f} {:8.2f} {:8.2f}'.format('precision:', stats_inc[0], stats_exc[0], stats_oth[0]))
print('{:12s} {:8.2f} {:8.2f} {:8.2f}'.format('recall:', stats_inc[1], stats_exc[1], stats_oth[1]))
print('{:12s} {:8.2f} {:8.2f} {:8.2f}'.format('f-measure:', stats_inc[2], stats_exc[2], stats_oth[2]))

# close down the script
source_data.close()
filtered_data.close()
log_include.close()
log_exclude.close()
log_other.close()
print('\napply and assess finished\n')
