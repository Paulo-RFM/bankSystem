import pika
import json
from datetime import datetime
from myBank.Account import Account  # Importe a classe Account onde você gerencia as contas
import uuid

def processar_transferencia(ch, method, properties, body):
    dados_transferencia = json.loads(body)
    print(f"Recebendo transferência: {dados_transferencia}")
    
    chave_pix_destino = dados_transferencia["chave_pix_destino"]
    valor = dados_transferencia["valor"]
    banco_origem = dados_transferencia["banco_origem"]
    chave_pix_remetente = dados_transferencia["chave_pix_remetente"]
    
    account = Account.get_pix_keys(chave_pix_destino)
    if not account:
        print("Conta não encontrada.")
        return
    
    new_balance = account.balance + valor
    Account.update_balance(account.account_number, new_balance)

    transfer_id = uuid.uuid4()
    Account.inserir_historico(
        transfer_id=transfer_id,
        account_number=account.account_number,
        pixKey_r=chave_pix_remetente,
        pixKey_d=chave_pix_destino,
        valor=valor,
        created_at=datetime.now()
    )
    
    print(f"Transferência processada com sucesso para a conta {account.account_number}.")

def iniciar_consumidor():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    
    channel.queue_declare(queue='transacoes_meu_banco')
    
    channel.basic_consume(queue='transacoes_meu_banco', on_message_callback=processar_transferencia, auto_ack=True)
    
    print('Aguardando transferências externas...')
    channel.start_consuming()
