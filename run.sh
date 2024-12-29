#!/bin/bash
# Menjalankan Flask
nohup python app.py &

# Menjalankan Ngrok menggunakan path lengkap
nohup /C:/ngrok/ngrok http 5000 &
