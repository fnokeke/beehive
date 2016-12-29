"""
Populate database with sample data
"""

from rep.models import MobileUser


def main():
    add_dummy_mobile_users(20)


def add_dummy_mobile_users(count=5):
    for k in range(count):
        i = k + 1
        info = {
            'email': 'dummy{}@gmail.com'.format(str(i)),
            'firstname': 'firstname{}'.format(str(i)),
            'lastname': 'lastname{}'.format(str(i)),
            'code': 'mobile'
        }
        MobileUser.add_user(info)
    print 'Successfully added {} users'.format(count)


if __name__ == '__main__':
    main()
