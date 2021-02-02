# Script to create RBAC access rules for the IEEE 1547 points RBAC access is created for based on the
# recommendations in J. Johnson, “Recommendations for Distributed Energy Resource Access Control,”
# Sandia Technical Report SAND2021-0977, 2021.
#
# Comments to jjohns2@sandia.gov

import json
import os

read_path = os.getcwd() + os.path.sep + 'json'
write_path = os.getcwd() + os.path.sep + 'rbac_json'
# print(read_path)

rbac_roles = [
    'der_owner',
    'installer',
    'der_vendor_or_service_provider',
    '3rd_party_or_aggregator',
    'utility_or_dso',
    'iso_rto_tso',
    'security_administrator',
    'security_auditor',
    'rbac_administrator',
]

rbac_no_write = {'der_owner': 'R',
                  'installer': 'R',
                  'der_vendor_or_service_provider': 'R',
                  '3rd_party_or_aggregator': 'R',
                  'utility_or_dso': 'R',
                  'iso_rto_tso': 'R',
                  'security_administrator': 'R',
                  'security_auditor': 'R',
                  'rbac_administrator': 'R'}

rbac_read = {'der_owner': 'R',
             'installer': 'R',
             'der_vendor_or_service_provider': 'R',
             '3rd_party_or_aggregator': 'R',
             'utility_or_dso': 'R',
             'iso_rto_tso': 'R',
             'security_administrator': '',
             'security_auditor': '',
             'rbac_administrator': ''}

rbac_install_and_control = {'der_owner': 'R',
                            'installer': 'RW',
                            'der_vendor_or_service_provider': 'R',
                            '3rd_party_or_aggregator': 'RW',
                            'utility_or_dso': 'RW',
                            'iso_rto_tso': 'RW',
                            'security_administrator': '',
                            'security_auditor': '',
                            'rbac_administrator': ''}

rbac_grid_control = {'der_owner': '',
                     'installer': 'R',
                     'der_vendor_or_service_provider': 'R',
                     '3rd_party_or_aggregator': 'RW',
                     'utility_or_dso': 'RW',
                     'iso_rto_tso': 'R',
                     'security_administrator': '',
                     'security_auditor': '',
                     'rbac_administrator': ''}

rbac_ride_through = {'der_owner': '',
                     'installer': 'RW',
                     'der_vendor_or_service_provider': 'R',
                     '3rd_party_or_aggregator': 'RW',
                     'utility_or_dso': 'RW',
                     'iso_rto_tso': 'R',
                     'security_administrator': '',
                     'security_auditor': '',
                     'rbac_administrator': ''}


def add_rbac(model, pt):
    # Don't give access to Modbus registers that contain SunSpec Modbus functionality
    if pt.get('name') == 'ID' or pt.get('name') == 'L' or pt.get('label') == 'Pad':
        pt['rbac'] = rbac_no_write

    # Don't adjust the scale factors for any points - assume these are fixed for the DER lifetime
    if pt.get('name')[-3:] == '_SF':
        pt['rbac'] = rbac_no_write

    else:
        if model == 1:  # Common
            pt['rbac'] = rbac_read

        if model == 701:
            pt['rbac'] = rbac_read

        if model == 702:  # DERCapacity
            if pt.get('name')[-3:] == 'Rtg' or pt.get('name') == 'CtrlModes' or pt.get('name') == 'IntIslandCat':
                pt['rbac'] = rbac_read
            else:  # Configuration/Settings
                pt['rbac'] = rbac_install_and_control

        if model == 703:  # DEREnterService
            if pt.get('name') == 'ES':
                pt['rbac'] = {'der_owner': 'R',
                              'installer': 'RW',
                              'der_vendor_or_service_provider': 'R',
                              '3rd_party_or_aggregator': 'R',
                              'utility_or_dso': 'RW',
                              'iso_rto_tso': 'RW',
                              'security_administrator': '',
                              'security_auditor': '',
                              'rbac_administrator': ''}
            else:
                pt['rbac'] = rbac_grid_control

        if model == 704:  # DERCtlAC
            pt['rbac'] = rbac_grid_control

        if model == 705:  # DERVoltVar
            pt['rbac'] = rbac_grid_control

        if model == 706:  # DERVoltWatt
            pt['rbac'] = rbac_grid_control

        # DERTripLV, DERTripHV, DERTripLF, DERTripHF
        if model == 707 or model == 708 or model == 709 or model == 710:
            pt['rbac'] = rbac_ride_through

        if model == 711:  # DERFreqDroop
            pt['rbac'] = rbac_grid_control

        if model == 712:  # DERWattVar
            pt['rbac'] = rbac_grid_control

        if model == 713:  # DERMeasureDC
            pt['rbac'] = rbac_read

    print(pt)


def main():
    # Only for the IEEE 1547 models right now
    for model in [1] + list(range(701, 714, 1)):
        with open(read_path + os.path.sep + 'model_%s.json' % model) as f:
            data = json.load(f)

        # print(json.dumps(data, indent=4, sort_keys=True))

        print('-' * 40)
        print('Model: %s [%s]' % (model, data.get('group').get('label')))
        print('-' * 40)

        for pt in data.get('group').get('points'):
            add_rbac(model, pt)

        # address groups separately
        if data.get('group').get('groups') is not None:
            for group in data.get('group').get('groups'):
                for pt in group.get('points'):
                    add_rbac(model, pt)

                if group.get('groups') is not None:
                    for group2 in group.get('groups'):  # groups of groups, e.g., VV curve points
                        for pt in group2.get('points'):
                            add_rbac(model, pt)

        # Write the python dict as new json file
        with open(write_path + os.path.sep + 'model_%s.json' % model, 'w') as json_file:
            json.dump(data, json_file, indent=4)


if __name__ == '__main__':
    main()
