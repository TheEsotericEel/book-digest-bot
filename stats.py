"""BookDigest Bot - Statistics Dashboard"""
import database as db
from datetime import datetime, timedelta

def print_stats():
    """Print comprehensive bot statistics"""
    print("=" * 60)
    print("BOOKDIGEST BOT - STATISTICS DASHBOARD")
    print("=" * 60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get stats from database
    stats = db.get_stats()
    
    # === USER METRICS ===
    print("USER METRICS")
    print("-" * 60)
    print(f"Total Users:           {stats['total_users']}")
    print(f"  - Free Users:        {stats['free_users']}")
    print(f"  - Pro Users:         {stats['pro_users']}")
    
    if stats['total_users'] > 0:
        pro_percentage = (stats['pro_users'] / stats['total_users']) * 100
        print(f"\nConversion Rate:       {pro_percentage:.1f}%")
    
    print()
    
    # === CONTENT METRICS ===
    print("CONTENT METRICS")
    print("-" * 60)
    print(f"Summaries Cached:      {stats['total_summaries']}")
    print(f"Total Accesses:        {stats['total_accesses']}")
    
    if stats['total_summaries'] > 0:
        avg_accesses = stats['total_accesses'] / stats['total_summaries']
        print(f"Avg Accesses/Summary:  {avg_accesses:.1f}")
    
    print()
    
    # === REVENUE METRICS ===
    print("REVENUE METRICS")
    print("-" * 60)
    print(f"Total Stars Collected: {stats['total_revenue_stars']}")
    print(f"Estimated USD:         ${stats['total_revenue_usd']:.2f}")
    
    # Monthly projections
    monthly_pro = stats['pro_users'] * 500  # 500 Stars per pro user per month
    monthly_usd = monthly_pro * 0.02
    
    print(f"\nMonthly Projection:")
    print(f"  Expected Stars:      {monthly_pro}")
    print(f"  Expected USD:        ${monthly_usd:.2f}")
    
    yearly_usd = monthly_usd * 12
    print(f"\nYearly Projection:")
    print(f"  Expected USD:        ${yearly_usd:.2f}")
    
    print()
    
    # === ENGAGEMENT ===
    print("ENGAGEMENT")
    print("-" * 60)
    
    if stats['total_users'] > 0:
        summaries_per_user = stats['total_accesses'] / stats['total_users']
        print(f"Avg Summaries/User:    {summaries_per_user:.1f}")
    
    print()
    
    # === HEALTH CHECK ===
    print("SYSTEM HEALTH")
    print("-" * 60)
    
    # Check database integrity
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Check for users with negative credits
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE credits < 0")
        negative_credits = cursor.fetchone()['count']
        
        # Check for orphaned records
        cursor.execute("""
            SELECT COUNT(*) as count FROM user_summaries us
            LEFT JOIN users u ON us.user_id = u.telegram_id
            WHERE u.telegram_id IS NULL
        """)
        orphaned_records = cursor.fetchone()['count']
        
        conn.close()
        
        health_issues = []
        if negative_credits > 0:
            health_issues.append(f"[!] {negative_credits} users with negative credits")
        if orphaned_records > 0:
            health_issues.append(f"[!] {orphaned_records} orphaned access records")
        
        if health_issues:
            for issue in health_issues:
                print(issue)
        else:
            print("[OK] All systems healthy")
    
    except Exception as e:
        print(f"[ERROR] Health check failed: {e}")
    
    print()
    
    # === GROWTH TARGETS ===
    print("GROWTH TARGETS")
    print("-" * 60)
    
    # Target: 10 paying users
    users_needed = max(0, 10 - stats['pro_users'])
    
    if stats['pro_users'] >= 10:
        print("[SUCCESS] TARGET ACHIEVED: 10+ paying users!")
    else:
        print(f"Target: 10 paying users")
        print(f"Current: {stats['pro_users']} pro users")
        print(f"Needed: {users_needed} more")
        
        # Estimate users needed based on conversion rate
        if stats['total_users'] > 0 and stats['pro_users'] > 0:
            conversion_rate = stats['pro_users'] / stats['total_users']
            total_users_needed = int(10 / conversion_rate)
            more_users_needed = max(0, total_users_needed - stats['total_users'])
            print(f"\nEstimated total users needed: {total_users_needed}")
            print(f"More users to acquire: {more_users_needed}")
    
    print()
    
    # === RECOMMENDATIONS ===
    print("RECOMMENDATIONS")
    print("-" * 60)
    
    recommendations = []
    
    if stats['total_users'] < 50:
        recommendations.append("Focus on user acquisition - share in communities")
    
    if stats['total_users'] > 0:
        conversion = (stats['pro_users'] / stats['total_users']) * 100
        if conversion < 10:
            recommendations.append("Improve conversion rate - test pricing or add features")
    
    if stats['total_accesses'] > 0 and stats['total_users'] > 0:
        engagement = stats['total_accesses'] / stats['total_users']
        if engagement < 2:
            recommendations.append("Low engagement - improve onboarding or content quality")
    
    if not recommendations:
        recommendations.append("Keep growing! Things are looking good")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    # Initialize DB if needed
    try:
        print_stats()
    except Exception as e:
        print(f"[ERROR] Error generating stats: {e}")
        print("\nMake sure the database is initialized:")
        print("  python database.py")
