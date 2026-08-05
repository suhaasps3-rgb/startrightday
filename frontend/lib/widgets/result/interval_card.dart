// lib/widgets/result/interval_card.dart
// Premium card displaying a single auspicious time interval.

import 'package:flutter/material.dart';
import '../../models/recommendation_result.dart';
import '../../theme/app_theme.dart';
import 'activity_chip.dart';
import 'panchang_detail_row.dart';

class IntervalCard extends StatefulWidget {
  final TimeInterval interval;
  final int index;

  const IntervalCard({
    super.key,
    required this.interval,
    required this.index,
  });

  @override
  State<IntervalCard> createState() => _IntervalCardState();
}

class _IntervalCardState extends State<IntervalCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _animController;
  late Animation<double> _fadeAnim;
  late Animation<Offset> _slideAnim;
  bool _expanded = false;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      duration: Duration(milliseconds: 400 + widget.index * 80),
      vsync: this,
    );
    _fadeAnim = CurvedAnimation(
      parent: _animController,
      curve: Curves.easeOut,
    );
    _slideAnim = Tween<Offset>(
      begin: const Offset(0, 0.08),
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: _animController, curve: Curves.easeOut));

    // Staggered entrance
    Future.delayed(Duration(milliseconds: widget.index * 60), () {
      if (mounted) _animController.forward();
    });
  }

  @override
  void dispose() {
    _animController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: _fadeAnim,
      child: SlideTransition(
        position: _slideAnim,
        child: Container(
          margin: const EdgeInsets.only(bottom: AppSpacing.md),
          decoration: BoxDecoration(
            color: AppColors.surfaceWhite,
            borderRadius: BorderRadius.circular(AppRadius.lg),
            border: Border.all(color: AppColors.border, width: 1),
            boxShadow: AppShadows.card,
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(AppRadius.lg),
            child: Column(
              children: [
                // ── Header ──────────────────────────────────────────────────
                _buildHeader(),

                // ── Divider ─────────────────────────────────────────────────
                const Divider(height: 1),

                // ── Panchang details ────────────────────────────────────────
                _buildPanchangSection(),

                // ── Activities ──────────────────────────────────────────────
                if (widget.interval.activities.isNotEmpty)
                  _buildActivitiesSection(),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.all(AppSpacing.md),
      child: Row(
        children: [
          // Time range
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Best Time Window',
                  style: AppTextStyles.labelSmall.copyWith(
                    color: AppColors.auspicious,
                    letterSpacing: 0.8,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '${widget.interval.startTime} – ${widget.interval.endTime}',
                  style: AppTextStyles.timeDisplay,
                ),
              ],
            ),
          ),
          // Status badge
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
            decoration: BoxDecoration(
              color: AppColors.auspiciousSurface,
              borderRadius: BorderRadius.circular(AppRadius.full),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 6,
                  height: 6,
                  decoration: const BoxDecoration(
                    color: AppColors.auspicious,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 5),
                Text(
                  'Recommended',
                  style: AppTextStyles.labelSmall.copyWith(
                    color: AppColors.auspicious,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 0.2,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPanchangSection() {
    final p = widget.interval.panchang;
    return Padding(
      padding: const EdgeInsets.fromLTRB(
        AppSpacing.md,
        AppSpacing.sm,
        AppSpacing.md,
        AppSpacing.sm,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'PANCHANG DETAILS',
            style: AppTextStyles.labelSmall.copyWith(letterSpacing: 1.2),
          ),
          const SizedBox(height: AppSpacing.sm),
          PanchangDetailRow(label: 'Nakshatra', value: p.nakshatra),
          PanchangDetailRow(label: 'Tara', value: p.tara),
          PanchangDetailRow(label: 'Tithi', value: p.tithi),
          PanchangDetailRow(label: 'Yoga', value: p.yoga),
          PanchangDetailRow(label: 'Karana', value: p.karana),
        ],
      ),
    );
  }

  Widget _buildActivitiesSection() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(
        AppSpacing.md,
        AppSpacing.sm,
        AppSpacing.md,
        AppSpacing.md,
      ),
      decoration: const BoxDecoration(
        color: AppColors.surfaceGray,
        border: Border(top: BorderSide(color: AppColors.border, width: 1)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'GOOD FOR',
            style: AppTextStyles.labelSmall.copyWith(letterSpacing: 1.2),
          ),
          const SizedBox(height: AppSpacing.sm),
          Wrap(
            spacing: AppSpacing.xs,
            runSpacing: AppSpacing.xs,
            children: widget.interval.activities
                .map((a) => ActivityChip(label: a))
                .toList(),
          ),
        ],
      ),
    );
  }
}
