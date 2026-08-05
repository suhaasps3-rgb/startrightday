// lib/screens/onboarding_screen.dart
// Clean 3-slide onboarding. No astrology framing — pure productivity app language.

import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../widgets/common/primary_button.dart';

class _OnboardingSlide {
  final String emoji;
  final String title;
  final String subtitle;

  const _OnboardingSlide({
    required this.emoji,
    required this.title,
    required this.subtitle,
  });
}

const _slides = [
  _OnboardingSlide(
    emoji: '🕐',
    title: 'Timing Is\nEverything',
    subtitle:
        'Starting at the right moment increases your chances of success. Classical Indian timekeeping has studied this for centuries.',
  ),
  _OnboardingSlide(
    emoji: '📋',
    title: 'Enter Your\nDetails Once',
    subtitle:
        'Just your birth place, date, and time. We use this to calculate the most aligned windows for your activities.',
  ),
  _OnboardingSlide(
    emoji: '✅',
    title: 'Get Clear\nRecommendations',
    subtitle:
        'No scores. No predictions. Just simple, rule-based guidance: the best time to begin — and why.',
  ),
];

class OnboardingScreen extends StatefulWidget {
  final VoidCallback onFinish;

  const OnboardingScreen({super.key, required this.onFinish});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final PageController _pageController = PageController();
  int _currentPage = 0;

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  void _next() {
    if (_currentPage < _slides.length - 1) {
      _pageController.nextPage(
        duration: const Duration(milliseconds: 350),
        curve: Curves.easeInOut,
      );
    } else {
      widget.onFinish();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Column(
          children: [
            // Skip button
            Align(
              alignment: Alignment.topRight,
              child: Padding(
                padding: const EdgeInsets.fromLTRB(0, AppSpacing.md, AppSpacing.md, 0),
                child: TextButton(
                  onPressed: widget.onFinish,
                  child: Text(
                    'Skip',
                    style: AppTextStyles.bodyMedium.copyWith(
                      color: AppColors.textSecondary,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ),
            ),

            // Slides
            Expanded(
              child: PageView.builder(
                controller: _pageController,
                onPageChanged: (i) => setState(() => _currentPage = i),
                itemCount: _slides.length,
                itemBuilder: (context, index) {
                  return _buildSlide(_slides[index]);
                },
              ),
            ),

            // Bottom controls
            Padding(
              padding: const EdgeInsets.fromLTRB(
                AppSpacing.lg,
                AppSpacing.lg,
                AppSpacing.lg,
                AppSpacing.xl,
              ),
              child: Column(
                children: [
                  // Dots
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: List.generate(_slides.length, (i) {
                      return AnimatedContainer(
                        duration: const Duration(milliseconds: 250),
                        margin: const EdgeInsets.symmetric(horizontal: 4),
                        width: _currentPage == i ? 24 : 8,
                        height: 8,
                        decoration: BoxDecoration(
                          color: _currentPage == i
                              ? AppColors.accent
                              : AppColors.border,
                          borderRadius: BorderRadius.circular(AppRadius.full),
                        ),
                      );
                    }),
                  ),

                  const SizedBox(height: AppSpacing.lg),

                  PrimaryButton(
                    label: _currentPage == _slides.length - 1
                        ? 'Get Started'
                        : 'Continue',
                    onPressed: _next,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSlide(_OnboardingSlide slide) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: AppSpacing.xl),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Emoji in a soft container
          Container(
            width: 72,
            height: 72,
            decoration: BoxDecoration(
              color: AppColors.accentSurface,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Center(
              child: Text(slide.emoji, style: const TextStyle(fontSize: 34)),
            ),
          ),

          const SizedBox(height: AppSpacing.xl),

          Text(
            slide.title,
            style: AppTextStyles.displayLarge.copyWith(height: 1.15),
          ),

          const SizedBox(height: AppSpacing.md),

          Text(
            slide.subtitle,
            style: AppTextStyles.bodyLarge.copyWith(
              color: AppColors.textSecondary,
              height: 1.7,
            ),
          ),
        ],
      ),
    );
  }
}
