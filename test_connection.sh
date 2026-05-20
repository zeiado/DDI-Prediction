#!/bin/bash

# Test Backend Connection Script

echo "=========================================="
echo "🧪 Testing Backend Connection"
echo "=========================================="
echo ""

# Test 1: Check if backend is running
echo "Test 1: Checking if backend is running..."
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Backend is running!"
else
    echo "❌ Backend is NOT running!"
    echo ""
    echo "Start it with:"
    echo "  cd /home/zeiado/DDI-Prediction/Backend"
    echo "  ./start_server.sh"
    exit 1
fi

echo ""

# Test 2: Check health endpoint
echo "Test 2: Checking health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:5000/health)
echo "Response: $HEALTH_RESPONSE"

if echo "$HEALTH_RESPONSE" | grep -q "\"online\":true"; then
    echo "✅ Health check passed!"
else
    echo "❌ Health check failed!"
    exit 1
fi

echo ""

# Test 3: Check drug search
echo "Test 3: Testing drug search..."
SEARCH_RESPONSE=$(curl -s "http://localhost:5000/search-drugs?q=war")
echo "Response: $SEARCH_RESPONSE"

if echo "$SEARCH_RESPONSE" | grep -q "Warfarin"; then
    echo "✅ Drug search working!"
else
    echo "❌ Drug search failed!"
    exit 1
fi

echo ""

# Test 4: Get computer IP
echo "Test 4: Getting your computer's IP address..."
COMPUTER_IP=$(hostname -I | awk '{print $1}')
echo "Your computer's IP: $COMPUTER_IP"
echo ""
echo "📱 For Physical Device, use this in Flutter:"
echo "   static const String baseUrl = 'http://$COMPUTER_IP:5000';"

echo ""

# Test 5: Check if port is accessible
echo "Test 5: Checking if port 5000 is accessible..."
if netstat -tuln | grep -q ":5000"; then
    echo "✅ Port 5000 is open and listening!"
else
    echo "⚠️  Port 5000 might not be accessible externally"
fi

echo ""
echo "=========================================="
echo "✅ ALL TESTS PASSED!"
echo "=========================================="
echo ""
echo "Your backend is working correctly!"
echo ""
echo "Device Configuration:"
echo "  📱 Android Emulator: http://10.0.2.2:5000"
echo "  📱 Physical Device:  http://$COMPUTER_IP:5000"
echo "  💻 iOS Simulator:    http://localhost:5000"
echo "  🌐 Web Browser:      http://localhost:5000"
echo ""
echo "Next steps:"
echo "  1. Make sure Flutter constants.dart has correct URL"
echo "  2. Run: flutter run"
echo "  3. Press 'R' to hot restart if needed"
echo ""
