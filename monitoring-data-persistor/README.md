### Necessary steps:
To further develop the component, some changes might be needed. Specifically, the  NEBULOUS_BASE_NAME might need to be changed in the library code connecting the component with  the broker.


### Interacting with the influx cli:

```bash
influx config create --config-name nebulous_conf \
  --host-url http://localhost:8086 \
  --org nebulous \
  --token tq5pA5uyt3pk65g9fALRZbMXCNg-81bDXuWK3NmjAyQN-t_cT3zFAbHzhtSeX83mJ1PqwZmeXALfKfdvDlGhVQ== \
  --active

```