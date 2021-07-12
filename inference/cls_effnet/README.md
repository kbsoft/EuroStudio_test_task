# Сборка


Сборка докер-образа  с нашими изменениями:
```
# DOCKER_BUILDKIT - нужно для сборки pytorch
DOCKER_BUILDKIT=1 docker build -t cls_effnet .
