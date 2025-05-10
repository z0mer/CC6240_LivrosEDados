# Esquema de mensagens

Cada mensagem JSON terá:
- `entity`: "cliente" | "livro" | "pedido"
- `action`: "create" | "update" | "delete" | "read"
- `payload`: objeto com os dados específicos

Exemplo:
```json
{
  "entity": "cliente",
  "action": "create",
  "payload": {
    "id": 1,
    "nome": "Ana Silva",
    "email": "ana.silva@example.com"
  }
}
