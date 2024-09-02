import requests
from flask import session

def login_core():
    try:
        response = requests.post(
            "https://projetosdufv.live/auth/",
            headers={"Content-Type": "application/json"},
            json={
                "instituicao_id": "206f65e1-a83a-4f35-8885-eaf1ee9b3cf2",
                "instituicao_secret": "T10_P@u!oB@nk#2024$S3cur3"
            }
        )
        
        if response.status_code == 200:
            print('token na mao')
            data = response.json()
            return data['access_token']
        else:
            print(f"Falha na autenticação com o core: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao tentar se conectar ao core: {e}")
        return None

