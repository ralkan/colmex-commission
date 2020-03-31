import argparse
from decimal import Decimal
from collections import namedtuple

parser = argparse.ArgumentParser()
parser.add_argument('file', type=str)

args = parser.parse_args()

tsv_fields = ('time symbol side price shares clr_type clr_broker '
              'acc type token note')
TSVField = namedtuple('TSVField', tsv_fields)
csv_fields = ('acc date curr type side symbol shares price time comm sec_fee '
              'taf_fee ecn_fee routing_fee nscc_fee clr_type clr_broker note')
CSVField = namedtuple('CSVField', csv_fields)

print(args.file)

lines = []

dt_list = args.file.split('.')[0].split('_')[1:]
new_file_name = "trades_{}.csv".format('_'.join(dt_list))
print(new_file_name)

dt = "{}/{}/{}".format(dt_list[1], dt_list[2], dt_list[0])

with open(args.file, 'r') as f:
    with open(new_file_name, 'w') as r:
        r.write("Account,Trade Date,Currency,Account Type,Side,Symbol,Shares,"
                "Price,Exec Time,Commission,SEC Fee,TAF Fee,ECN Fee,"
                "Routing Fee,NSCC Fee,Clr Type, Clr Broker,Note\n")
        for line in f:
            line = map(lambda l: l.replace('"', ''),
                       line.replace('\n', '').split('\t'))

            tsv_fields = TSVField(*line)._asdict()
            del tsv_fields['token']
            fields = CSVField(
                curr="USD",
                date=dt,
                comm="0",
                sec_fee="0",
                taf_fee="0",
                ecn_fee="0",
                routing_fee="0",
                nscc_fee="0",
                **tsv_fields)

            commission = Decimal(fields.shares) * Decimal('0.006')
            if commission < Decimal('1.5'):
                commission = Decimal('1.5')
            fields = fields._replace(
                comm=str(commission),
                routing_fee=str(Decimal(fields.shares) * Decimal('0.0015')))
            print(fields)

            new_line = ','.join(list(map(
                lambda cf: '"{}"'.format(getattr(fields, cf)),
                csv_fields.split(' '))))
            r.write(new_line.rstrip('""') + '\n')
