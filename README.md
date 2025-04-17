# Visão Noturna com Raspberry Pi e Mendix

Projeto completo que demonstra como criar um sistema de visão noturna usando um Raspberry Pi integrado com a plataforma Mendix para visualização e monitoramento remoto.

## O que o projeto faz?
- Captura imagens noturnas utilizando uma câmera IR conectada ao Raspberry Pi.
- Alterna automaticamente entre modo diurno e noturno com base no brilho ambiente.
- Detecta pessoas utilizando um detector HOG em tempo real.
- Realiza streaming ao vivo das imagens processadas via Flask.
- Envia automaticamente imagens com detecção de pessoas para a aplicação Mendix através de um Web Service REST.

## Tecnologias Utilizadas
- Raspberry Pi
- Python (Flask, OpenCV, Picamera2)
- Plataforma Mendix

## Arquitetura

![Arquitetura do Projeto](https://raw.githubusercontent.com/unifgabsantos/Night-Vision/refs/heads/main/Arquitetura.jpg)



## Pré-requisitos
- Raspberry Pi configurado com Raspberry Pi OS.
- Câmera compatível com Raspberry Pi (preferencialmente com capacidade infravermelha).
- Instalação do ambiente Python com as dependências necessárias.

### Dependências Python
Instale as dependências usando:
```bash
pip install flask opencv-python numpy picamera2 requests
```

## Executando o projeto
1. Clone este repositório:

```bash
git clone https://github.com/unifgabsantos/Night-Vision
cd Night-Vision
```

2. Execute o script principal:

```bash
sudo python3 main.py
```

3. Acesse o streaming ao vivo em:
```
http://<IP_DO_RASPBERRY_PI>/
```

## Integração Mendix

- Configure um Web Service REST em sua aplicação Mendix para receber imagens detectadas e exibi-las em um dashboard interativo.
- A URL configurada no código Python (`MENDIX_UPLOAD_URL`) deve corresponder ao endpoint criado na aplicação Mendix.

## Estrutura do Projeto

```
.
├── main.py (script Python principal)
├── README.md (este arquivo)
└── MPK (Projeto Mendix)
```

## Autor
- **Gabriel Lopes Parreira dos Santos** - [GitHub](https://github.com/unifgabsantos/)
