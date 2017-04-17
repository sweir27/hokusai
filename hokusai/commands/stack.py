import os

from collections import OrderedDict

import yaml

from hokusai.command import command
from hokusai.config import config
from hokusai.common import print_red, print_green, shout
from hokusai.deployment import Deployment
from hokusai.service import Service
from hokusai.kubectl import Kubectl
from hokusai.secret import Secret

@command
def stack_create(context):
  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % context)
  if not os.path.isfile(kubernetes_yml):
    print_red("Yaml file %s does not exist for given context." % kubernetes_yml)
    return -1

  secret = Secret(context)
  secret.create()
  print_green("Created secret %s-secrets" % config.project_name)

  kctl = Kubectl(context)
  shout(kctl.command("apply -f %s" % kubernetes_yml))
  print_green("Created stack %s" % context)

@command
def stack_update(context):
  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % context)
  if not os.path.isfile(kubernetes_yml):
    print_red("Yaml file %s does not exist for given context." % kubernetes_yml)
    return -1

  kctl = Kubectl(context)
  shout(kctl.command("apply -f %s" % kubernetes_yml))
  print_green("Updated stack %s" % context)

@command
def stack_delete(context):
  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % context)
  if not os.path.isfile(kubernetes_yml):
    print_red("Yaml file %s does not exist for given context." % kubernetes_yml)
    return -1

  secret = Secret(context)
  secret.destroy()
  print_green("Deleted secret %s-secrets" % config.project_name)

  kctl = Kubectl(context)
  shout(kctl.command("delete -f %s" % kubernetes_yml))
  print_green("Deleted stack %s" % context)

@command
def stack_status(context):
  deployment = Deployment(context)
  deployment_data = []
  for item in deployment.cache:
    deployment_data.append(OrderedDict([
      ('name', item['metadata']['name']),
      ('desiredReplicas', item['spec']['replicas']),
      ('availableReplicas', item['status']['availableReplicas'] if 'availableReplicas' in item['status'] else 0),
      ('unavailableReplicas', item['status']['unavailableReplicas'] if 'unavailableReplicas' in item['status'] else 0),
      ('tag', deployment.current_tag)
    ]))

  service = Service(context)
  service_data = []
  for item in service.cache:
    service_data.append(OrderedDict([
      ('target', item['spec']['selector']['app']),
      ('clusterIP', item['spec']['clusterIP']),
      ('ports', item['spec']['ports']),
      ('status', item['status'])
    ]))
  print('')
  print_green("Stack %s status" % context)
  print('')
  print_green("Deployments")
  print_green('-----------------------------------------------------------')
  print(yaml.safe_dump(deployment_data, default_flow_style=False))

  print_green("Services")
  print_green('-----------------------------------------------------------')
  print(yaml.safe_dump(service_data, default_flow_style=False))
