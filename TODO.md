# TODO

## Instance IDs inexistants dans kube endpoint
- poller les endpoints k8 toutes les 50 minutes (voir plus fréquement)
- effectuer la mise en liaison de current->instanceId avec kube->instanceId à posteriori des insertions indépendantes de chaque tables (dynamic_instance & dim_kubernetes) OU effectuer à l'insertion de nouvelles données dans dim_kube

## Gérer les savings plan
- init. table savingsPlan pour chaque savingsPlanId dans la liste

### Over quota
init. une instance dynamique pour l'over quota du savings:
    - récupérer flavor en suivant les savingsPlanIds pour s'assurer que ce dernier est fiable (reference définie à la main ?)
    - beaucoup d'attributs à vide dans le tuple de l'instance dynamique créee pour l'over quota... (pas de: dep_mode, resource_id, instance_id donc pas de dim kube)