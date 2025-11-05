import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'onboarding_screen.dart';
import 'terms_screen.dart';
import 'auth_screen.dart';
import 'home_screen.dart';

class VideoSplashScreen extends StatefulWidget {
  const VideoSplashScreen({Key? key}) : super(key: key);

  @override
  State<VideoSplashScreen> createState() => _VideoSplashScreenState();
}

class _VideoSplashScreenState extends State<VideoSplashScreen> {
  late VideoPlayerController _controller;
  bool _isInitialized = false;

  @override
  void initState() {
    super.initState();
    _initializeVideo();
  }

  Future<void> _initializeVideo() async {
    _controller = VideoPlayerController.asset('assets/videos/splash.mp4');
    
    try {
      await _controller.initialize();
      setState(() {
        _isInitialized = true;
      });
      
      // Start playing
      await _controller.play();
      
      // Listen for video completion
      _controller.addListener(() {
        if (_controller.value.position >= _controller.value.duration) {
          _navigateToNextScreen();
        }
      });
    } catch (e) {
      print('Error initializing video: $e');
      // If video fails, navigate after a delay
      Future.delayed(const Duration(seconds: 2), () {
        _navigateToNextScreen();
      });
    }
  }

  void _navigateToNextScreen() async {
    if (!mounted) return;
    
    final prefs = await SharedPreferences.getInstance();
    final onboardingComplete = prefs.getBool('onboarding_complete') ?? false;
    final termsAccepted = prefs.getBool('terms_accepted') ?? false;
    
    Widget nextScreen;
    
    if (!onboardingComplete) {
      // First time user - show onboarding
      nextScreen = const OnboardingScreen();
    } else if (!termsAccepted) {
      // Onboarding done but terms not accepted
      nextScreen = const TermsScreen();
    } else {
      // Check auth status
      final user = FirebaseAuth.instance.currentUser;
      nextScreen = user != null ? const HomeScreen() : const AuthScreen();
    }
    
    if (mounted) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => nextScreen),
      );
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: _isInitialized
          ? SizedBox.expand(
              child: FittedBox(
                fit: BoxFit.contain,
                child: SizedBox(
                  width: _controller.value.size.width,
                  height: _controller.value.size.height,
                  child: VideoPlayer(_controller),
                ),
              ),
            )
          : const Center(
              child: CircularProgressIndicator(
                color: Colors.white,
              ),
            ),
    );
  }
}
