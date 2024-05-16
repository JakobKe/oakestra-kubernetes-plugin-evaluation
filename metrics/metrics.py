import requests
import json
import csv
import os
from datetime import datetime, timedelta


PROMETHEUS_URL = 'http://localhost:9090/api/v1/query_range'
QUERY = 'sum(rate(container_network_transmit_packets_total[5m])) by (container, pod, namespace)'
END_TIME = datetime.now()
START_TIME = END_TIME - timedelta(minutes=5)
STEP = '1s'
CSV_FILE = 'prometheus_data_1.csv'


def query_prometheus(query, prometheus_url='http://localhost:9090'):
    response = requests.get(f'{prometheus_url}/api/v1/query', params={'query': query})
    response.raise_for_status()
    return response.json()

def query_prometheus_interval(query):
    """Holt Daten von Prometheus."""
    response = requests.get(PROMETHEUS_URL, params={
        'query': query,
        'start': START_TIME.timestamp(),
        'end': END_TIME.timestamp(),
        'step': STEP
    })
    response.raise_for_status()
    return response.json()

    
def save_to_csv(data, directory, filename):
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    filepath = os.path.join(directory, filename)
    
    with open(filepath, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        
        # Header dynamisch erstellen
        headers = set()
        for result in data['data']['result']:
            headers.update(result['metric'].keys())
        headers = list(headers)
        headers.extend(['timestamp', 'value'])
        
        # Schreibe die Header
        csv_writer.writerow(headers)
        
        # Schreibe die Datenzeilen
        for result in data['data']['result']:
            metric = result['metric']
            if 'value' in result:  # Einzelwert
                value = result['value']
                row = [metric.get(header, '') for header in headers if header not in ['timestamp', 'value']]
                row.extend([value[0], value[1]])
                csv_writer.writerow(row)
            elif 'values' in result:  # Mehrere Werte
                values = result['values']
                for value in values:
                    row = [metric.get(header, '') for header in headers if header not in ['timestamp', 'value']]
                    row.extend([value[0], value[1]])
                    csv_writer.writerow(row)
    
    print(f'CSV-File has been created: {filepath}')
    

def main():
    prometheus_url = 'http://localhost:9090'  # URL deines Prometheus-Servers
    directory = 'results/test'  # Ordnername
    
    ###############################
    ## CPU NODES
    ###############################
    directory = 'results/cpu_nodes'  
    
    query = 'avg(rate(node_cpu_seconds_total[5m]))'
    filename = 'nodes_cpu_seconds_total_5m.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    query = 'avg by (instance) (rate(node_cpu_seconds_total[5m]))'
    filename = 'node_cpu_seconds_total_5m_by_instance.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    query = 'avg(rate(node_cpu_seconds_total{mode="idle"}[5m]))'
    filename = 'nodes_cpu_seconds_idle_5m.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    query = 'avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m]))'
    filename = 'node_cpu_seconds_idle_5m_by_instance.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    
    query = 'avg(rate(container_cpu_usage_seconds_total[5m]))'
    filename = 'container_cpu_seconds_total_5m.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    query = 'avg by (instance, pod) (rate(container_cpu_usage_seconds_total[5m]))'
    filename = 'container_cpu_seconds_total_5m_by_instance.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    

    
    ###############################
    ## MEMORY NODE
    ###############################
    directory = 'results/memory_node'  
    
    query = 'avg by (instance)(container_memory_usage_bytes)'
    filename = 'container_memory_usage_bytes_by_instance.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    query = 'avg by (instance, pod) (container_memory_usage_bytes)'
    filename = 'container_memory_usage_bytes_by_instance_and_pod.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    
    query = 'avg by (instance) ((node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100)'
    filename = 'node_memory_used_by_instance.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    ###############################
    ## MEMORY CONTAINER
    ###############################
    directory = 'results/memory_container' 
    SELECTED_PODS = "kube-apiserver.*|metrics-server.*"
    SELECTED_NAMESPACE = "default|kube-system" 

    query = f'avg(container_memory_usage_bytes{{pod=~"{SELECTED_PODS}", namespace=~"{SELECTED_NAMESPACE}"}}) by (pod, namespace)'
    filename = f'container_memory_usage_bytes--pods:{SELECTED_PODS}.csv'
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    query = f'avg(avg_over_time(container_memory_usage_bytes{{pod=~"{SELECTED_PODS}"}}[5m]))'
    filename = f'sum_selected_container_memory_usage_bytes--pods:{SELECTED_PODS}.csv'
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    query = f'avg by (pod, namespace) (avg_over_time(container_memory_usage_bytes{{pod=~"{SELECTED_PODS}"}}[5m]))'
    filename = f'selected_container_memory_usage_bytes--pods:{SELECTED_PODS}.csv'
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    
    
    
    ###############################
    ## CPU CONTAINER
    ###############################
    directory = 'results/cpu_container'
    SELECTED_PODS = "kube-apiserver.*|metrics-server.*"
    SELECTED_NAMESPACE = "default|kube-system" 
    
    query = 'sum(rate(container_cpu_usage_seconds_total[5m]))'
    filename = 'container_cpu_usage_seconds_total.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    query = 'sum by (pod) (rate(container_cpu_usage_seconds_total[5m]))'
    filename = 'container_cpu_usage_seconds_total_per_pod.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    query = f'sum by (pod) (rate(container_cpu_usage_seconds_total{{pod=~"{SELECTED_PODS}"}}[5m]))'
    filename = f'container_cpu_usage_seconds_total--pods:{SELECTED_PODS}.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    
    
    
    

    ###############################
    ## NETWORK
    ###############################
    directory = 'results/network' 
    
    query = 'sum(rate(container_network_transmit_packets_total[5m])) by (container, pod, namespace)'
    filename = 'network_transmit_packets.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)

    query = 'sum(rate(container_network_transmit_bytes_total[5m])) by (container, pod, namespace)'
    filename = 'network_transmit_bytes.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    query = 'sum(rate(container_network_receive_packets_total[5m])) by (container, pod, namespace)'
    filename = 'network_received_packets.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)

    query = 'sum(rate(container_network_receive_bytes_total[5m])) by (container, pod, namespace)'
    filename = 'network_received_bytes.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    
    
    ###############################
    ## API SERVER AND METRICS SERVER
    ###############################
    SELECTED_PODS = "kube-apiserver.*|metrics-server.*"
    directory = 'results/api_metrics' 
    
    
    query = f'avg(container_memory_usage_bytes{{pod=~"{SELECTED_PODS}"}}) by (pod, namespace)'
    filename = f'container_memory_usage_bytes--pods:{SELECTED_PODS}.csv'
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    query = f'sum(avg_over_time(container_memory_usage_bytes{{pod=~"{SELECTED_PODS}"}}[5m])) by (pod, namespace)'
    filename = 'sum_container_memory_usage_bytes--pods:{SELECTED_PODS}.csv'
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    

if __name__ == '__main__':
    main()




