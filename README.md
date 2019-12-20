# zabbix-protocol

## About

Simple python3 module that sends data with the Zabbix protocol headers.

* https://zabbix.com
* https://www.zabbix.com/documentation/current/manual/appendix/protocols/header\_datalen

## Example

```
$ echo '{"request": "active checks", "host": "server.example.com"}' | python3 zabbix_proto.py zabbix.example.com 10051 | jq
{
  "response": "success",
  "data": [
    {
      "key": "test[123]",
      "delay": 30,
      "lastlogsize": 0,
      "mtime": 0
    }
  ]
}
```
