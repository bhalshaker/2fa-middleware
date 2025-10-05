## Prequesits

- Create a Twilio account and have a number
- Create Resend account

## Build and Start Environment Using Podman/Docker

- Clone the project

```sh
git clone https://github.com/bhalshaker/2fa-middleware.git
```

- Go to the project folder

```sh
cd 2fa-middleware

```

- Create .env file refere to example.env

- Build enviroment

```sh
podman compose build
```

- Start enviroment

```sh
podman compose up
```

## Start using the application

- Create a token using curl from keycloak you may refer to Sample Users table

```sh
curl --location 'http://localhost:8080/realms/2faproject/protocol/openid-connect/token' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'client_id=fastapi-client' \
--data-urlencode 'grant_type=password' \
--data-urlencode 'username=ebrahim.salem' \
--data-urlencode 'password=Ebrahim123' \
--data-urlencode 'client_secret=ZzX7oJoxnyXyuUGcAgWbFby8ma9dSkL2'
```

- Grap the token and Open FastAPI Swagger UI

```
http://localhost:8000/docs
```

- Place the token in Authorize

- Go to POST method of users to create a record for the user in the database. Behind the sceen Swagger will create a similar request if you do not want to use swagger replace the token with the one generated to you.

```sh
curl -X 'POST' \
  'http://localhost:8000/user' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJTcWdsZkFfQjREV0M2VlJ0YUJ2X0c1LVEwc19YTERwQzlhQjVnS2FpbjZzIn0.eyJleHAiOjE3NTk2Nzk5NjIsImlhdCI6MTc1OTY3ODE2MiwianRpIjoib25ydHJvOjQ1MTlmMWRhLTcwZmItNWVkZC1mYjYyLTEzZTRhMjlmM2I5MSIsImlzcyI6Imh0dHA6Ly9sb2NhbGhvc3Q6ODA4MC9yZWFsbXMvMmZhcHJvamVjdCIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiJjZmRjZGQ3MS05OTcwLTRlMGQtYTY1MC1jZWNiMzQ3N2U5OTEiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJmYXN0YXBpLWNsaWVudCIsInNpZCI6ImQ0NTZmYWM2LTZjZTMtZGMzNS05YzY5LTExOTUyNjUwNWExYSIsImFjciI6IjEiLCJhbGxvd2VkLW9yaWdpbnMiOlsiLyoiXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iLCJkZWZhdWx0LXJvbGVzLTJmYXByb2plY3QiXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6ImVtYWlsIHByb2ZpbGUiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwibmFtZSI6IkVicmFoaW0gU2FsZW0iLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJlYnJhaGltLnNhbGVtIiwiZ2l2ZW5fbmFtZSI6IkVicmFoaW0iLCJmYW1pbHlfbmFtZSI6IlNhbGVtIiwiZW1haWwiOiJlYnJhaGltLnNhbGVtQGV4YW1wbGUuY29tIn0.Cxh8S97I6HpPLbUqTBorY0_4kFpYV1OliysW9En02ZqtPVLXaCXFWStA10-mCSsSv-OSNlxXj8qofdje6_2XacRpgsn6P7TJox8tlmpr894Syzck7UKv4HHi_AqCl_poj2ixFtuz4PHqLFiba9ympOWUPWuGMIT_f9YoCBjSfOEmyOsWM3p4frpv7ZWimNjhB7BOWPTtfXg9IrHo7cn4zshpIPf4Be5mg7Wqo5K6CvKP5EZOPjWdoZ6zsR69MWUeYcLGEB2y2I9kiDd_rTq8U_n1Sw0y2ta62_j0ZbDpsC7jX-Lq1lfUDd3u_75FK9OscBHLC_qRoaFJ7bxHidg8MA' \
  -d ''
```

### Sample Users

| Username      | First   | Last    | Email                     | Password   |
| ------------- | ------- | ------- | ------------------------- | ---------- |
| ebrahim.salem | Ebrahim | Salem   | ebrahim.salem@example.com | Ebrahim123 |
| layla.hassan  | Layla   | Hassan  | layla.hassan@example.com  | Layla456   |
| omar.farouk   | Omar    | Farouk  | omar.farouk@example.com   | Omar789    |
| sara.nasr     | Sara    | Nasr    | sara.nasr@example.com     | Sara321    |
| ali.zayed     | Ali     | Zayed   | ali.zayed@example.com     | Ali654     |
| noor.khalid   | Noor    | Khalid  | noor.khalid@example.com   | Noor987    |
| yousef.amir   | Yousef  | Amir    | yousef.amir@example.com   | Yousef111  |
| mariam.fahmy  | Mariam  | Fahmy   | mariam.fahmy@example.com  | Mariam222  |
| hassan.tariq  | Hassan  | Tariq   | hassan.tariq@example.com  | Hassan333  |
| dina.rami     | Dina    | Rami    | dina.rami@example.com     | Dina444    |
| khaled.nabil  | Khaled  | Nabil   | khaled.nabil@example.com  | Khaled555  |
| rania.adel    | Rania   | Adel    | rania.adel@example.com    | Rania666   |
| tamer.sami    | Tamer   | Sami    | tamer.sami@example.com    | Tamer777   |
| huda.mansour  | Huda    | Mansour | huda.mansour@example.com  | Huda888    |
| zain.mahmoud  | Zain    | Mahmoud | zain.mahmoud@example.com  | Zain999    |
| nour.yassin   | Nour    | Yassin  | nour.yassin@example.com   | Nour000    |
| bassam.hatem  | Bassam  | Hatem   | bassam.hatem@example.com  | Bassam101  |
| lina.sherif   | Lina    | Sherif  | lina.sherif@example.com   | Lina202    |
| walid.fadel   | Walid   | Fadel   | walid.fadel@example.com   | Walid303   |
| salma.gamal   | Salma   | Gamal   | salma.gamal@example.com   | Salma404   |
