from django.utils import timezone
from users.models import Company, DemandUser, ProviderUser
from django.contrib.auth import get_user_model
import random
from faker import Faker

fake = Faker('ko_KR')

def generate_fake_companies(num_companies=20):
    """가상의 회사 데이터 생성"""
    user_types = ['provider', 'demand']
    statuses = ['pending', 'approved', 'rejected']
    
    for _ in range(num_companies):
        user_type = random.choice(user_types)
        
        Company.objects.create(
            company_name=fake.company(),
            user_type=user_type,
            business_registration_number=fake.bothify(text='########-#######'),
            email=fake.email(),
            business_phone_number=fake.phone_number(),
            address=fake.address(),
            status=random.choice(statuses),
            created_at=fake.date_time_between(start_date='-2y', end_date='now', tzinfo=timezone.get_current_timezone()),
            updated_at=timezone.now()
        )

def generate_fake_demand_users(num_users=10):
    """가상의 수요자 사용자 데이터 생성"""
    User = get_user_model()
    
    for _ in range(num_users):
        username = fake.user_name()
        
        # 중복 방지
        while User.objects.filter(username=username).exists():
            username = fake.user_name()
        
        DemandUser.objects.create(
            username=username,
            email=fake.email(),
            company_name=fake.company(),
            is_active=random.choice([True, False]),
            is_approved=random.choice([True, False]),
            created_at=fake.date_time_between(start_date='-2y', end_date='now', tzinfo=timezone.get_current_timezone())
        )

def generate_fake_provider_users(num_users=10):
    """가상의 공급자 사용자 데이터 생성"""
    User = get_user_model()
    
    for _ in range(num_users):
        username = fake.user_name()
        
        # 중복 방지
        while User.objects.filter(username=username).exists():
            username = fake.user_name()
        
        ProviderUser.objects.create(
            username=username,
            email=fake.email(),
            company_name=fake.company(),
            business_registration_number=fake.bothify(text='########-#######'),
            business_phone_number=fake.phone_number(),
            is_active=random.choice([True, False]),
            is_approved=random.choice([True, False]),
            created_at=fake.date_time_between(start_date='-2y', end_date='now', tzinfo=timezone.get_current_timezone())
        )

def create_fake_data():
    """모든 가짜 데이터 생성"""
    # 기존 데이터 삭제 (선택사항)
    Company.objects.all().delete()
    DemandUser.objects.all().delete()
    ProviderUser.objects.all().delete()
    
    # 가짜 데이터 생성
    generate_fake_companies()
    generate_fake_demand_users()
    generate_fake_provider_users()

    print("✅ 가짜 데이터 생성 완료!")
