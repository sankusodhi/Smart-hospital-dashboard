#!/bin/bash

echo "🚀 Starting Flask App in background..."
nohup python app.py > flask.log 2>&1 &

sleep 3

echo "🌍 Starting Ngrok Tunnel in background..."
nohup ngrok http 5000 --domain=steadily-unsuperseded-christia.ngrok-free.dev > ngrok.log 2>&1 &

echo "✅ Demo server started!"
echo "🌐 Demo URL: https://steadily-unsuperseded-christia.ngrok-free.dev"

