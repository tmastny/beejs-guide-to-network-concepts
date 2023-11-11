# 22-project

## symlink to import

```
ln -s ../19-project/netfuncs.py netfuncs
```

## Routers

Routers in JSON:
- keys are ip addresses
- have property `connections`
- this is another json keyed by adjacent ip addresses

## Check

```
python dijkstra.py example1.json > output.txt
difft output.txt example1_output.txt
```
