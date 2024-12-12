# Cleanup scripts

Clean up any Helm releases that have created a resource with an annotation called "cloudbees/expiry".

```shell
python expired_releases.py
```

To add an expiration to your chart, you can add a template to your `_helpers.tpl` file:

```tpl
{{/*
Add an expiration X number of hours ahead
*/}}
{{- define "addHours" -}}
{{- $hours := mul (int .) 3600 -}}
{{- now | unixEpoch | add $hours | date "2006-01-02T15:04:05Z" -}}
{{- end -}}
```

And then in the resource YAML add an annotation like the following:

```yaml
metadata:
  name: {{ .Release.Name }}
  annotations:
    cloudbees/expiry: {{ template "addHours" 24 }}
```
