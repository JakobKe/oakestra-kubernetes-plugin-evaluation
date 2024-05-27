import requests
import json
import csv
import os
from datetime import datetime, timedelta



PROMETHEUS_URL = 'http://localhost:9090/api/v1/query_range'
STEP = '1s'

# Defined dataframe with start point. 
start_time_str = "2024-05-19 17:38:02.732487 +0200"
START_TIME = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S.%f %z")
START_TIME = START_TIME.replace(microsecond=0)
END_TIME = START_TIME + timedelta(minutes=5)


# # Most recent time
# END_TIME = datetime.now()
# START_TIME = END_TIME - timedelta(minutes=5)

print("START_TIME:", START_TIME)
print("END_TIME:", END_TIME)


def query_prometheus_interval(query):
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
    
    query = 'sum(rate(node_cpu_seconds_total[1m]))'
    filename = 'nodes_cpu_seconds_total_5m.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    query = 'sum by (instance) (rate(node_cpu_seconds_total[1m]))'
    filename = 'node_cpu_seconds_total_5m_by_instance.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    query = 'sum(rate(node_cpu_seconds_total{mode="idle"}[1m]))'
    filename = 'nodes_cpu_seconds_idle_5m.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    query = 'sum by (instance) (rate(node_cpu_seconds_total{mode="idle"}[1m]))'
    filename = 'node_cpu_seconds_idle_5m_by_instance.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
        
    query = 'sum by (instance, pod) (rate(container_cpu_usage_seconds_total[1m]))'
    filename = 'container_cpu_seconds_total_5m_by_instance.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    

    ###############################
    ## MEMORY NODE
    ###############################
    directory = 'results/memory_node'  
    
    query = 'sum by (instance)(container_memory_working_set_bytes)'
    filename = 'container_memory_working_set_bytes_by_instance.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    query = 'avg by (instance, pod) (container_memory_working_set_bytes)'
    filename = 'container_memory_working_set_bytes_by_instance_and_pod.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    query = 'avg by (instance) ((node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100)'
    filename = 'node_memory_used_by_instance.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    
    ###############################
    ## MEMORY CONTAINER/POD
    ###############################
    directory = 'results/memory_container' 
    
    SELECTED_PODS = ".*"
    SELECTED_NAMESPACE = "oakestra.*" 
    
    # SELECTED_PODS = "karmada-agent.*"
    # SELECTED_NAMESPACE = "karmada-system" 
    
    # SELECTED_PODS = "klusterlet.*"
    # SELECTED_NAMESPACE = "open-cluster-management.*" 
    

    query = f'sum(container_memory_working_set_bytes{{pod=~"{SELECTED_PODS}", namespace=~"{SELECTED_NAMESPACE}"}}) by (pod, namespace)'
    filename = f'container_memory_working_set_bytes--pods:{SELECTED_PODS}.csv'
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    # Hier hat nur der letzte Wert den gesamten Testlauf drin. 
    query = f'sum(avg_over_time(container_memory_working_set_bytes{{pod=~"{SELECTED_PODS}", namespace=~"{SELECTED_NAMESPACE}"}}[5m]))'
    filename = f'sum_selected_container_memory_working_set_bytes--pods:{SELECTED_PODS}.csv'
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    # Hier hat nur der letzte Wert den gesamten Testlauf drin. 
    query = f'sum by (pod, namespace) (avg_over_time(container_memory_working_set_bytes{{pod=~"{SELECTED_PODS}", namespace=~"{SELECTED_NAMESPACE}"}}[5m]))'
    filename = f'selected_container_memory_working_set_bytes--pods:{SELECTED_PODS}.csv'
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    
    
    ###############################
    ## CPU CONTAINER/POD
    ###############################
    directory = 'results/cpu_container'
    
    SELECTED_PODS = ".*"
    SELECTED_NAMESPACE = "oakestra.*" 
    
    
    # SELECTED_PODS = "karmada-agent.*"
    # SELECTED_NAMESPACE = "karmada-system"
    
    # SELECTED_PODS = "klusterlet.*"
    # SELECTED_NAMESPACE = "open-cluster-management.*"  
    
    query = 'sum(rate(container_cpu_usage_seconds_total[1m]))'
    filename = 'container_cpu_usage_seconds_total.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    query = 'sum by (pod, namespace) (rate(container_cpu_usage_seconds_total[1m]))'
    filename = 'container_cpu_usage_seconds_total_per_pod.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    # Redundant!
    query = f'sum by (pod, namespace) (rate(container_cpu_usage_seconds_total{{pod=~"{SELECTED_PODS}", namespace=~"{SELECTED_NAMESPACE}"}}[1m]))'
    filename = f'container_cpu_usage_seconds_total--pods:{SELECTED_PODS}.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    
    
    
    

    ###############################
    ## NETWORK
    ###############################
    directory = 'results/network' 
    
    query = 'sum(rate(container_network_transmit_packets_total[1m])) by (container, pod, namespace)'
    filename = 'network_transmit_packets.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)

    query = 'sum(rate(container_network_transmit_bytes_total[1m])) by (container, pod, namespace)'
    filename = 'network_transmit_bytes.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    query = 'sum(rate(container_network_receive_packets_total[1m])) by (container, pod, namespace)'
    filename = 'network_received_packets.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)

    query = 'sum(rate(container_network_receive_bytes_total[1m])) by (container, pod, namespace)'
    filename = 'network_received_bytes.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    
    
    ###############################
    ## API SERVER AND METRICS SERVER
    ###############################
    SELECTED_PODS = "kube-apiserver.*|metrics-server.*"
    directory = 'results/api_metrics' 
    
    
    query = f'sum by (pod, namespace) (rate(container_cpu_usage_seconds_total{{pod=~"{SELECTED_PODS}"}}[1m]))'
    filename = f'container_cpu_usage_seconds_total--pods:{SELECTED_PODS}.csv'  
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
    
    query = f'sum(container_memory_working_set_bytes{{pod=~"{SELECTED_PODS}", namespace=~"{SELECTED_NAMESPACE}"}}) by (pod, namespace)'
    filename = f'container_memory_working_set_bytes--pods:{SELECTED_PODS}.csv'
    data = query_prometheus_interval(query)
    save_to_csv(data, directory, filename)
        
    

if __name__ == '__main__':
    main()




