"""
Management command to load dummy academic data using Faker
"""
import random
from datetime import datetime, timedelta, time
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker
from apps.academics.models import (
    AcademicYear, Term, SchoolClass, Section, Subject, 
    ClassSubject, TimeTable, House
)
from apps.users.models import User


class Command(BaseCommand):
    help = 'Load dummy academic data using Faker'

    def __init__(self):
        super().__init__()
        self.fake = Faker()
        self.current_year = datetime.now().year
        
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing academic data before loading',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing academic data...'))
            self.clear_data()

        try:
            with transaction.atomic():
                self.stdout.write('Creating academic data...')
                
                # Create academic years
                academic_years = self.create_academic_years()
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(academic_years)} academic years'))
                
                # Create terms
                terms = self.create_terms(academic_years)
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(terms)} terms'))
                
                # Create houses
                houses = self.create_houses()
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(houses)} houses'))
                
                # Create classes
                classes = self.create_classes()
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(classes)} classes'))
                
                # Create sections
                sections = self.create_sections(classes)
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(sections)} sections'))
                
                # Create subjects
                subjects = self.create_subjects()
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(subjects)} subjects'))
                
                # Assign subjects to classes
                class_subjects = self.assign_subjects_to_classes(classes, subjects, academic_years[0])
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(class_subjects)} class-subject assignments'))
                
                # Create timetables
                timetables = self.create_timetables(sections, class_subjects, academic_years[0])
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(timetables)} timetable entries'))
                
                self.stdout.write(self.style.SUCCESS('\n✓ Successfully loaded all academic dummy data!'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            raise

    def clear_data(self):
        """Clear existing academic data"""
        TimeTable.objects.all().delete()
        ClassSubject.objects.all().delete()
        Section.objects.all().delete()
        Subject.objects.all().delete()
        SchoolClass.objects.all().delete()
        House.objects.all().delete()
        Term.objects.all().delete()
        AcademicYear.objects.all().delete()

    def create_academic_years(self):
        """Create academic years"""
        academic_years = []
        
        for i in range(3):  # Current, previous, and next year
            year = self.current_year - 1 + i
            start_date = datetime(year, 4, 1).date()
            end_date = datetime(year + 1, 3, 31).date()
            
            academic_year, created = AcademicYear.objects.get_or_create(
                code=f'AY{year}-{year+1}',
                defaults={
                    'name': f'Academic Year {year}-{year+1}',
                    'start_date': start_date,
                    'end_date': end_date,
                    'is_current': (i == 1),  # Middle year is current
                    'has_terms': True,
                }
            )
            academic_years.append(academic_year)
            
        return academic_years

    def create_terms(self, academic_years):
        """Create terms for academic years"""
        terms = []
        term_types = ['FIRST_TERM', 'SECOND_TERM', 'THIRD_TERM']
        term_names = ['First Term', 'Second Term', 'Third Term']
        
        for academic_year in academic_years:
            year_start = academic_year.start_date
            
            for i, (term_type, term_name) in enumerate(zip(term_types, term_names)):
                # Calculate term dates (roughly 3-4 months each)
                start_date = year_start + timedelta(days=i * 120)
                end_date = start_date + timedelta(days=110)
                
                term, created = Term.objects.get_or_create(
                    academic_year=academic_year,
                    term_type=term_type,
                    defaults={
                        'name': term_name,
                        'order': i + 1,
                        'start_date': start_date,
                        'end_date': end_date,
                        'is_current': (academic_year.is_current and i == 0),
                    }
                )
                terms.append(term)
                
        return terms

    def create_houses(self):
        """Create school houses"""
        house_data = [
            {'name': 'Red House', 'code': 'RED', 'color': '#FF0000', 'motto': 'Courage and Strength'},
            {'name': 'Blue House', 'code': 'BLUE', 'color': '#0000FF', 'motto': 'Wisdom and Knowledge'},
            {'name': 'Green House', 'code': 'GREEN', 'color': '#00FF00', 'motto': 'Growth and Harmony'},
            {'name': 'Yellow House', 'code': 'YELLOW', 'color': '#FFFF00', 'motto': 'Energy and Joy'},
        ]
        
        houses = []
        for data in house_data:
            house, created = House.objects.get_or_create(
                code=data['code'],
                defaults=data
            )
            houses.append(house)
            
        return houses

    def create_classes(self):
        """Create school classes"""
        classes = []
        class_data = [
            # Pre-Primary
            ('Nursery', 0, 'NUR', 'PRE_PRIMARY', 1),
            ('LKG', 0, 'LKG', 'PRE_PRIMARY', 2),
            ('UKG', 0, 'UKG', 'PRE_PRIMARY', 3),
            # Primary
            ('Class 1', 1, 'CLS1', 'PRIMARY', 4),
            ('Class 2', 2, 'CLS2', 'PRIMARY', 5),
            ('Class 3', 3, 'CLS3', 'PRIMARY', 6),
            ('Class 4', 4, 'CLS4', 'PRIMARY', 7),
            ('Class 5', 5, 'CLS5', 'PRIMARY', 8),
            # Middle
            ('Class 6', 6, 'CLS6', 'MIDDLE', 9),
            ('Class 7', 7, 'CLS7', 'MIDDLE', 10),
            ('Class 8', 8, 'CLS8', 'MIDDLE', 11),
            # High
            ('Class 9', 9, 'CLS9', 'HIGH', 12),
            ('Class 10', 10, 'CLS10', 'HIGH', 13),
            # Senior
            ('Class 11', 11, 'CLS11', 'SENIOR', 14),
            ('Class 12', 12, 'CLS12', 'SENIOR', 15),
        ]
        
        for name, numeric, code, level, order in class_data:
            # Get a random teacher if available
            teachers = User.objects.filter(role='teacher')
            class_teacher = random.choice(teachers) if teachers.exists() else None
            
            school_class, created = SchoolClass.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'numeric_name': numeric if numeric > 0 else 1,
                    'level': level,
                    'order': order,
                    'max_strength': random.choice([30, 35, 40, 45]),
                    'tuition_fee': random.randint(5000, 15000),
                    'class_teacher': class_teacher,
                    'is_active': True,
                }
            )
            classes.append(school_class)
            
        return classes

    def create_sections(self, classes):
        """Create sections for classes"""
        sections = []
        section_names = ['A', 'B', 'C', 'D']
        
        for school_class in classes:
            # Primary and above get 2-3 sections, pre-primary gets 1-2
            num_sections = 2 if school_class.level == 'PRE_PRIMARY' else 3
            
            for i in range(num_sections):
                section_name = section_names[i]
                
                # Get a random teacher if available
                teachers = User.objects.filter(role='teacher')
                section_incharge = random.choice(teachers) if teachers.exists() else None
                
                section, created = Section.objects.get_or_create(
                    class_name=school_class,
                    name=section_name,
                    defaults={
                        'code': f'{school_class.code}-{section_name}',
                        'max_strength': school_class.max_strength,
                        'section_incharge': section_incharge,
                        'room_number': f'{school_class.order}{section_name}',
                        'is_active': True,
                    }
                )
                sections.append(section)
                
        return sections

    def create_subjects(self):
        """Create subjects"""
        subjects = []
        subject_data = [
            # Core subjects
            ('English', 'ENG', 'CORE', 'GENERAL', True, False, 100, 33),
            ('Mathematics', 'MATH', 'CORE', 'GENERAL', True, False, 100, 33),
            ('Science', 'SCI', 'CORE', 'SCIENCE', True, True, 100, 33),
            ('Social Studies', 'SST', 'CORE', 'GENERAL', True, False, 100, 33),
            ('Hindi', 'HIN', 'LANGUAGE', 'GENERAL', True, False, 100, 33),
            
            # Science stream
            ('Physics', 'PHY', 'CORE', 'SCIENCE', True, True, 100, 33),
            ('Chemistry', 'CHEM', 'CORE', 'SCIENCE', True, True, 100, 33),
            ('Biology', 'BIO', 'CORE', 'SCIENCE', True, True, 100, 33),
            
            # Commerce stream
            ('Accountancy', 'ACC', 'CORE', 'COMMERCE', True, False, 100, 33),
            ('Business Studies', 'BS', 'CORE', 'COMMERCE', True, False, 100, 33),
            ('Economics', 'ECO', 'CORE', 'COMMERCE', True, False, 100, 33),
            
            # Arts stream
            ('History', 'HIST', 'CORE', 'ARTS', True, False, 100, 33),
            ('Geography', 'GEO', 'CORE', 'ARTS', True, False, 100, 33),
            ('Political Science', 'POL', 'CORE', 'ARTS', True, False, 100, 33),
            
            # Co-curricular
            ('Computer Science', 'CS', 'CO_CURRICULAR', 'GENERAL', True, True, 100, 33),
            ('Physical Education', 'PE', 'CO_CURRICULAR', 'GENERAL', False, False, 50, 17),
            ('Art & Craft', 'ART', 'EXTRA_CURRICULAR', 'GENERAL', False, False, 50, 17),
            ('Music', 'MUS', 'EXTRA_CURRICULAR', 'GENERAL', False, False, 50, 17),
        ]
        
        for name, code, subject_type, group, is_scoring, has_practical, max_marks, pass_marks in subject_data:
            subject, created = Subject.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'subject_type': subject_type,
                    'subject_group': group,
                    'has_practical': has_practical,
                    'is_scoring': is_scoring,
                    'credit_hours': random.randint(3, 6),
                    'max_marks': max_marks,
                    'pass_marks': pass_marks,
                    'is_active': True,
                }
            )
            subjects.append(subject)
            
        return subjects

    def assign_subjects_to_classes(self, classes, subjects, academic_year):
        """Assign subjects to classes"""
        class_subjects = []
        
        # Core subjects for all classes
        core_subjects = ['ENG', 'MATH', 'HIN']
        
        for school_class in classes:
            # Get teachers
            teachers = list(User.objects.filter(role='teacher'))
            
            # Assign core subjects
            for subject_code in core_subjects:
                subject = Subject.objects.get(code=subject_code)
                teacher = random.choice(teachers) if teachers else None
                
                class_subject, created = ClassSubject.objects.get_or_create(
                    class_name=school_class,
                    subject=subject,
                    academic_year=academic_year,
                    defaults={
                        'is_compulsory': True,
                        'periods_per_week': random.randint(5, 7),
                        'teacher': teacher,
                    }
                )
                class_subjects.append(class_subject)
            
            # Add level-specific subjects
            if school_class.level in ['PRIMARY', 'MIDDLE']:
                # Add Science and Social Studies
                for subject_code in ['SCI', 'SST']:
                    subject = Subject.objects.get(code=subject_code)
                    teacher = random.choice(teachers) if teachers else None
                    
                    class_subject, created = ClassSubject.objects.get_or_create(
                        class_name=school_class,
                        subject=subject,
                        academic_year=academic_year,
                        defaults={
                            'is_compulsory': True,
                            'periods_per_week': random.randint(4, 6),
                            'teacher': teacher,
                        }
                    )
                    class_subjects.append(class_subject)
            
            # Add co-curricular
            for subject_code in ['CS', 'PE']:
                try:
                    subject = Subject.objects.get(code=subject_code)
                    teacher = random.choice(teachers) if teachers else None
                    
                    class_subject, created = ClassSubject.objects.get_or_create(
                        class_name=school_class,
                        subject=subject,
                        academic_year=academic_year,
                        defaults={
                            'is_compulsory': False,
                            'periods_per_week': random.randint(2, 3),
                            'teacher': teacher,
                        }
                    )
                    class_subjects.append(class_subject)
                except Subject.DoesNotExist:
                    pass
                    
        return class_subjects

    def create_timetables(self, sections, class_subjects, academic_year):
        """Create timetable entries"""
        timetables = []
        days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
        
        # School timings
        periods = [
            (1, time(8, 0), time(8, 45)),
            (2, time(8, 45), time(9, 30)),
            (3, time(9, 30), time(10, 15)),
            (4, time(10, 30), time(11, 15)),  # After break
            (5, time(11, 15), time(12, 0)),
            (6, time(12, 0), time(12, 45)),
            (7, time(13, 30), time(14, 15)),  # After lunch
            (8, time(14, 15), time(15, 0)),
        ]
        
        # Create timetable for a few sections (to avoid too much data)
        sample_sections = random.sample(list(sections), min(10, len(sections)))
        
        for section in sample_sections:
            # Get subjects for this class
            subjects_for_class = list(ClassSubject.objects.filter(
                class_name=section.class_name,
                academic_year=academic_year
            ))
            
            if not subjects_for_class:
                continue
                
            for day in days:
                for period_num, start_time, end_time in periods:
                    # Skip some periods randomly (breaks, etc.)
                    if random.random() < 0.2:
                        continue
                        
                    # Pick a random subject
                    class_subject = random.choice(subjects_for_class)
                    
                    try:
                        timetable, created = TimeTable.objects.get_or_create(
                            class_name=section.class_name,
                            section=section,
                            day=day,
                            period_number=period_num,
                            academic_year=academic_year,
                            defaults={
                                'start_time': start_time,
                                'end_time': end_time,
                                'subject': class_subject,
                                'teacher': class_subject.teacher,
                                'room': section.room_number,
                                'period_type': 'PRACTICAL' if class_subject.subject.has_practical and random.random() < 0.3 else 'LECTURE',
                            }
                        )
                        if created:
                            timetables.append(timetable)
                    except Exception as e:
                        # Skip if there's a conflict
                        continue
                        
        return timetables
