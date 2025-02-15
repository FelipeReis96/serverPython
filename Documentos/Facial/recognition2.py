import cv2
import os
import numpy as np

# Verifique se a pasta "faces" existe, se não, crie-a
if not os.path.exists("faces"):
    os.makedirs("faces")

# Função para capturar e salvar imagens de rostos
def capturar_rostos():
    cap = cv2.VideoCapture(0)
    
    # Verifique se a câmera foi aberta corretamente
    if not cap.isOpened():
        print("Erro: Não foi possível acessar a câmera.")
        return

    id_pessoa = input("Digite seu ID (número): ")
    count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro ao capturar o quadro. Tentando novamente...")
            continue
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rosto_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        rostos = rosto_cascade.detectMultiScale(gray, 1.1, 4)

        for (x, y, w, h) in rostos:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            rosto = gray[y:y+h, x:x+w]
            cv2.imwrite(f"faces/{id_pessoa}_{count}.jpg", rosto)
            print(f"Imagem {count} salva com ID {id_pessoa}")
            count += 1

        # Exibe a imagem capturada
        cv2.imshow("Captura de Rosto", frame)

        # Se pressionar a tecla 'q', sai do loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Para quando 10 imagens forem capturadas (ajustado para mais imagens)
        if count >= 10:
            print("Captura de rostos concluída!")
            break
    
    cap.release()
    cv2.destroyAllWindows()

# Função para treinar o modelo com as imagens salvas
def treinar_reconhecimento():
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    # Carregar as imagens de treino
    caminhos_imagens = []
    ids = []

    # Leitura das imagens na pasta 'faces'
    for root, dirs, files in os.walk('faces'):
        for file in files:
            if file.endswith(".jpg"):
                caminhos_imagens.append(os.path.join(root, file))
                id = int(file.split('_')[0])  # A primeira parte do nome do arquivo é o ID
                ids.append(id)

    # Ler as imagens e treinar o modelo
    imagens = []
    for caminho in caminhos_imagens:
        img = cv2.imread(caminho, cv2.IMREAD_GRAYSCALE)
        imagens.append(img)

    # Treinar o modelo
    recognizer.train(imagens, np.array(ids))
    recognizer.save('modelo_face.yml')  # Salvar o modelo treinado

    print("Modelo treinado e salvo!")

# Função de reconhecimento
def reconhecer_rosto():
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    # Carregar o modelo treinado
    recognizer.read('modelo_face.yml')

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Erro: Não foi possível acessar a câmera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro ao capturar o quadro. Tentando novamente...")
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rosto_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        rostos = rosto_cascade.detectMultiScale(gray, 1.1, 4)

        for (x, y, w, h) in rostos:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            rosto = gray[y:y+h, x:x+w]
            id_pred, conf = recognizer.predict(rosto)

            # Ajuste de confiança
            if conf < 50:  # Limite ajustado de confiança para melhorar a precisão
                cv2.putText(frame, f"ID: {id_pred} - Reconhecido", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "Desconhecido", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        cv2.imshow("Reconhecimento de Rosto", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Passos do programa
capturar_rostos()  # Captura as imagens para treinamento
treinar_reconhecimento()  # Treina o modelo com as imagens capturadas
reconhecer_rosto()  # Reconhece rostos ao vivo com a câmera





























