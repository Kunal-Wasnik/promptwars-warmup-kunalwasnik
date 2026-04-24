# API Contract — [Feature Name]

## 📝 Instructions
Use this file as the "Source of Truth" for any data exchanged between the FastAPI backend and the Vanilla JS frontend.

---

## Endpoint: [METHOD] `/path`
### Request
- **Headers**: `Content-Type: application/json`
- **Body**:
```json
{
  "key": "value"
}
```

### Response (200 OK)
- **Body**:
```json
{
  "status": "success",
  "data": {}
}
```

### Mock Data (For Frontend Prototyping)
```json
{
  "status": "success",
  "data": []
}
```
