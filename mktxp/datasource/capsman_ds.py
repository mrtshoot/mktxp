# coding=utf8
## Copyright (c) 2020 Arseniy Kuznetsov
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.


from mktxp.datasource.base_ds import BaseDSProcessor
from mktxp.datasource.wireless_ds import WirelessMetricsDataSource


class CapsmanInfo:
    @staticmethod
    def capsman_path(router_entry):
        if WirelessMetricsDataSource.is_legacy(router_entry):
            return '/caps-man'
        else:
            wireless_package = WirelessMetricsDataSource.wireless_package(router_entry)
            return f'/interface/{wireless_package}/capsman'

    @staticmethod
    def registration_table_path(router_entry):
        if WirelessMetricsDataSource.is_legacy(router_entry):
            return '/caps-man/registration-table'
        else:
            wireless_package = WirelessMetricsDataSource.wireless_package(router_entry)
            return f'/interface/{wireless_package}/registration-table'

class CapsmanCapsMetricsDataSource:
    ''' Caps Metrics data provider
    '''             
    @staticmethod
    def metric_records(router_entry, *, metric_labels = None):
        if metric_labels is None:
            metric_labels = []                
        try:
            capsman_path = CapsmanInfo.capsman_path(router_entry)
            remote_caps_records = router_entry.api_connection.router_api().get_resource(f'{capsman_path}/remote-cap').get()
            return BaseDSProcessor.trimmed_records(router_entry, router_records = remote_caps_records, metric_labels = metric_labels)
        except Exception as exc:
            print(f'Error getting CAPsMAN remote caps info from router{router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None


class CapsmanRegistrationsMetricsDataSource:
    ''' Capsman Registrations Metrics data provider
    '''             
    @staticmethod
    def metric_records(router_entry, *, metric_labels = None,  add_router_id = True):
        if metric_labels is None:
            metric_labels = []                
        try:
            registration_table_path = CapsmanInfo.registration_table_path(router_entry)
            registration_table_records = router_entry.api_connection.router_api().get_resource(f'{registration_table_path}').get()
            
            # With wifiwave2, Mikrotik renamed the field 'rx-signal' to 'signal' 
            # For backward compatibility, including both variants
            for record in registration_table_records:
                if 'signal' in record:
                    record['rx-signal'] = record['signal']

            return BaseDSProcessor.trimmed_records(router_entry, router_records = registration_table_records, metric_labels = metric_labels, add_router_id = add_router_id)
        except Exception as exc:
            print(f'Error getting CAPsMAN registration table info from router{router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None


class CapsmanInterfacesDatasource:
    ''' Data provider for CAPsMaN interfaces
    '''

    @staticmethod
    def metric_records(router_entry, *, metric_labels = None):
        if not WirelessMetricsDataSource.is_legacy(router_entry):
            return None            
        if metric_labels is None:
            metric_labels = []                
        try:
            caps_interfaces = router_entry.api_connection.router_api().get_resource('/caps-man/interface').get()
            return BaseDSProcessor.trimmed_records(router_entry, router_records = caps_interfaces, metric_labels = metric_labels)
        except Exception as exc:
            print(f'Error getting CAPsMAN interfaces info from router{router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None
