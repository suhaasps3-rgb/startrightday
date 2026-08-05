// lib/screens/result_screen.dart
// Displays the recommendation result: auspicious intervals or avoid state.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/recommendation_result.dart';
import '../providers/recommendation_provider.dart';
import '../theme/app_theme.dart';
import '../widgets/common/primary_button.dart';
import '../widgets/result/interval_card.dart';

class ResultScreen extends ConsumerWidget {
  final VoidCallback onBack;

  const ResultScreen({super.key, required this.onBack});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(recommendationProvider);

    return state.when(
      loading: () => const _LoadingPlaceholder(),
      error: (error, _) => _ErrorView(
        message: error is Exception ? error.toString() : 'Something went wrong.',
        onRetry: onBack,
      ),
      data: (result) {
        if (result == null) {
          return _ErrorView(message: 'No data available.', onRetry: onBack);
        }
        return _ResultContent(result: result, onBack: onBack);
      },
    );
  }
}

// ---------------------------------------------------------------------------
// Main result content
// ---------------------------------------------------------------------------
class _ResultContent extends StatelessWidget {
  final RecommendationResult result;
  final VoidCallback onBack;

  const _ResultContent({required this.result, required this.onBack});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: CustomScrollView(
          physics: const BouncingScrollPhysics(),
          slivers: [
            SliverToBoxAdapter(child: _buildTopBar(context)),
            SliverToBoxAdapter(child: _buildStatusBanner()),
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(
                  AppSpacing.lg,
                  0,
                  AppSpacing.lg,
                  AppSpacing.sm,
                ),
                child: _buildDateMeta(),
              ),
            ),
            if (result.isAuspicious)
              SliverPadding(
                padding: const EdgeInsets.symmetric(horizontal: AppSpacing.lg),
                sliver: SliverList(
                  delegate: SliverChildBuilderDelegate(
                    (context, i) => IntervalCard(
                      interval: result.intervals[i],
                      index: i,
                    ),
                    childCount: result.intervals.length,
                  ),
                ),
              )
            else
              SliverToBoxAdapter(child: _buildEmptyState()),

            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.all(AppSpacing.lg),
                child: PrimaryButton(
                  label: 'Check Another Date',
                  onPressed: onBack,
                ),
              ),
            ),
            const SliverToBoxAdapter(child: SizedBox(height: AppSpacing.lg)),
          ],
        ),
      ),
    );
  }

  Widget _buildTopBar(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(
        AppSpacing.sm,
        AppSpacing.md,
        AppSpacing.lg,
        0,
      ),
      child: Row(
        children: [
          IconButton(
            icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 20),
            color: AppColors.textPrimary,
            onPressed: onBack,
          ),
          const Spacer(),
          Text(
            'StartRightDay',
            style: AppTextStyles.labelLarge.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusBanner() {
    final isAuspicious = result.isAuspicious;
    final bgColor =
        isAuspicious ? AppColors.auspiciousSurface : AppColors.avoidSurface;
    final fgColor = isAuspicious ? AppColors.auspicious : AppColors.avoid;
    final label = isAuspicious ? 'Auspicious Day' : 'Avoid New Starts';
    final icon = isAuspicious ? Icons.check_circle_outline : Icons.remove_circle_outline;

    return Container(
      margin: const EdgeInsets.fromLTRB(
        AppSpacing.lg,
        AppSpacing.lg,
        AppSpacing.lg,
        AppSpacing.md,
      ),
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(AppRadius.lg),
      ),
      child: Row(
        children: [
          Icon(icon, color: fgColor, size: 28),
          const SizedBox(width: AppSpacing.md),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: AppTextStyles.headlineMedium.copyWith(color: fgColor),
              ),
              if (result.birthNakshatra != null)
                Text(
                  'Birth Nakshatra: ${result.birthNakshatra}',
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: fgColor.withOpacity(0.75),
                    fontSize: 12,
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildDateMeta() {
    if (result.activityDateDisplay == null) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.sm),
      child: Text(
        result.activityDateDisplay!,
        style: AppTextStyles.bodyMedium.copyWith(
          fontWeight: FontWeight.w600,
          color: AppColors.textSecondary,
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Padding(
      padding: const EdgeInsets.all(AppSpacing.xl),
      child: Column(
        children: [
          const SizedBox(height: AppSpacing.xxl),
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: AppColors.avoidSurface,
              borderRadius: BorderRadius.circular(24),
            ),
            child: const Center(
              child: Text('🌙', style: TextStyle(fontSize: 36)),
            ),
          ),
          const SizedBox(height: AppSpacing.lg),
          Text(
            'No Auspicious Time Found',
            style: AppTextStyles.headlineMedium,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: AppSpacing.sm),
          Text(
            result.message ??
                'No auspicious time found today. Consider choosing a different date.',
            style: AppTextStyles.bodyLarge.copyWith(
              color: AppColors.textSecondary,
              height: 1.7,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Error state
// ---------------------------------------------------------------------------
class _ErrorView extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;

  const _ErrorView({required this.message, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: const Color(0xFFFEE2E2),
                  borderRadius: BorderRadius.circular(24),
                ),
                child: const Center(
                  child: Text('⚠️', style: TextStyle(fontSize: 36)),
                ),
              ),
              const SizedBox(height: AppSpacing.lg),
              Text('Something went wrong', style: AppTextStyles.headlineMedium),
              const SizedBox(height: AppSpacing.sm),
              Text(
                message.replaceAll('Exception: ', ''),
                style: AppTextStyles.bodyLarge.copyWith(
                  color: AppColors.textSecondary,
                  height: 1.7,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: AppSpacing.xxl),
              PrimaryButton(label: 'Go Back', onPressed: onRetry),
            ],
          ),
        ),
      ),
    );
  }
}

class _LoadingPlaceholder extends StatelessWidget {
  const _LoadingPlaceholder();

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      backgroundColor: AppColors.background,
      body: Center(
        child: CircularProgressIndicator(color: AppColors.accent),
      ),
    );
  }
}
