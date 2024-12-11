docker_build('nguu0123/web-server', 'src/web-server')
docker_build('nguu0123/pre-processor', 'src/pre-processor')
docker_build('nguu0123/inference-server', 'src/inference-server')

k8s_yaml('src/deployment/web.yml')
k8s_yaml('src/deployment/preproc.yml')
k8s_yaml('src/deployment/inf.yml')
k8s_yaml('src/deployment/jaeger.yml')

k8s_resource('web-server', port_forwards=8000)
k8s_resource('jaeger', port_forwards=16686)

