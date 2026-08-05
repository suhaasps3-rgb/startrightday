// lib/screens/loading_screen.dart
// Beautiful animated loading screen with cycling Panchang messages.

import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/recommendation_provider.dart';
import '../theme/app_theme.dart';

const _messages = [
  'Calculating Panchang...',
  'Finding Nakshatra...',
  'Checking Tarabalam...',
  'Filtering Rahu Kalam...',
  'Applying Vedic rules...',
  'Generating Recommendation...',
];

class LoadingScreen extends ConsumerStatefulWidget {
  final VoidCallback onResult;
  final VoidCallback onError;

  const LoadingScreen({
    super.key,
    required this.onResult,
    required this.onError,
  });

  @override
  ConsumerState<LoadingScreen> createState() => _LoadingScreenState();
}

class _LoadingScreenState extends ConsumerState<LoadingScreen>
    with TickerProviderStateMixin {
  int _messageIndex = 0;
  Timer? _messageTimer;
  bool _navigated = false;

  // Arc animation
  late AnimationController _arcController;
  // Message fade animation
  late AnimationController _msgController;
  late Animation<double> _msgFadeAnim;

  @override
  void initState() {
    super.initState();

    // Rotating arc
    _arcController = AnimationController(
      duration: const Duration(milliseconds: 1200),
      vsync: this,
    )..repeat();

    // Message fade
    _msgController = AnimationController(
      duration: const Duration(milliseconds: 400),
      vsync: this,
    )..forward();
    _msgFadeAnim = CurvedAnimation(parent: _msgController, curve: Curves.easeInOut);

    // Cycle messages every 1.1s
    _messageTimer = Timer.periodic(const Duration(milliseconds: 1100), (_) {
      _msgController.reverse().then((_) {
        if (mounted) {
          setState(() {
            _messageIndex = (_messageIndex + 1) % _messages.length;
          });
          _msgController.forward();
        }
      });
    });
  }

  @override
  void dispose() {
    _messageTimer?.cancel();
    _arcController.dispose();
    _msgController.dispose();
    super.dispose();
  }

  // Watch provider and navigate when done
  void _handleStateChange(AsyncValue result) {
    if (_navigated) return;
    result.whenOrNull(
      data: (data) {
        if (data != null) {
          _navigated = true;
          WidgetsBinding.instance.addPostFrameCallback((_) => widget.onResult());
        }
      },
      error: (_, __) {
        _navigated = true;
        WidgetsBinding.instance.addPostFrameCallback((_) => widget.onError());
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(recommendationProvider);
    _handleStateChange(state);

    return Scaffold(
      backgroundColor: AppColors.background,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.xl),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Custom arc loader
              _buildArcLoader(),
              const SizedBox(height: AppSpacing.xxl),

              // App name
              Text(
                'StartRightDay',
                style: AppTextStyles.headlineMedium.copyWith(
                  color: AppColors.primary,
                ),
              ),
              const SizedBox(height: AppSpacing.sm),

              // Cycling message
              FadeTransition(
                opacity: _msgFadeAnim,
                child: Text(
                  _messages[_messageIndex],
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.textSecondary,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildArcLoader() {
    return SizedBox(
      width: 80,
      height: 80,
      child: RotationTransition(
        turns: _arcController,
        child: CustomPaint(
          painter: _ArcPainter(),
        ),
      ),
    );
  }
}

class _ArcPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 6;

    // Background track
    final trackPaint = Paint()
      ..color = AppColors.border
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4
      ..strokeCap = StrokeCap.round;

    canvas.drawCircle(center, radius, trackPaint);

    // Gradient arc
    final rect = Rect.fromCircle(center: center, radius: radius);
    final shader = const SweepGradient(
      colors: [Color(0xFF6366F1), Color(0xFF818CF8), Color(0xFFEEF2FF)],
      stops: [0.0, 0.6, 1.0],
    ).createShader(rect);

    final arcPaint = Paint()
      ..shader = shader
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      rect,
      -1.5708, // Start at top (-π/2)
      4.0,     // ~230° arc
      false,
      arcPaint,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
