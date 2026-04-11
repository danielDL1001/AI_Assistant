# Assistant

Assistente de leitura de notificações em voz alta, em segundo plano.

## Recursos implementados

- Leitura contínua de notificações no Linux (DBus).
- Pipeline de fala em **background** (fila + thread dedicada).
- Suporte a voz clonada com `audio/reference.wav` via XTTS (`VOICE_MODE = "clone"`).
- Reprodução compatível com Linux e Windows no módulo de TTS.
- Modo de retorno de repouso: ao detectar volta de suspensão, o assistente coleta notificações por alguns segundos e então fala:
  - resumo com quantidade + conteúdo; ou
  - mensagem de ausência de notificações.

## Execução

```bash
python scripts/run_assistant.py
```

## Configuração

Ajuste em `scripts/config.py`:

- `VOICE_MODE`: `clone` ou `light`
- `SUSPEND_GAP_SECONDS`: sensibilidade para detectar retorno de suspensão
- `RESUME_COLLECTION_SECONDS`: janela de coleta após retorno
- `USER_NAME` e templates de fala

## Observações de plataforma

- Captura de notificações: Linux implementado.
- Windows: pipeline de fala funciona, mas captura nativa de notificações ainda está como placeholder