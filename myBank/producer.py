import pika
import json

def enviar_transferencia_externa(chave_pix_destino, valor, banco_origem, chave_pix_remetente):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    
    fila = "transacoes_meu_banco"
    channel.queue_declare(queue=fila)
    
    dados_transferencia = {
        "chave_pix_destino": chave_pix_destino,
        "valor": valor,
        "banco_origem": banco_origem,
        "chave_pix_remetente": chave_pix_remetente
    }

    mensagem = json.dumps(dados_transferencia)
    channel.basic_publish(exchange='', routing_key=fila, body=mensagem)
    
    print(f"Transferência enviada: {mensagem}")
    
    connection.close()
