"""
Populate database with sample data
"""

from rep.models import Experiment, MobileUser


def main():
    info = {'code': 'mobile', 'count': 5, 'no_of_condition': 3, 'ps_per_condition': 3}
    add_dummy_experiment(info)
    add_dummy_mobile_users(info)

    info = {'code': 'shoutout', 'count': 5, 'no_of_condition': 3, 'ps_per_condition': 3}
    add_dummy_experiment(info)
    add_dummy_mobile_users(info)


def add_dummy_experiment(info):
    experiment = Experiment.query.filter_by(code=info['code']).first()
    if experiment:
        print 'Experiment (code={}) already exists'.format(info['code'])
        return

    experiment = {
        'title': 'dummy experiment ({})'.format(info['code']),
        'rescuetime': True,
        'aware': True,
        'geofence': True,
        'text': True,
        'image': True,
        'reminder': True,
        'actuators': True,
        'code': info['code'],
        'no_of_condition': info['no_of_condition'],
        'ps_per_condition': info['ps_per_condition']
    }

    Experiment.add_experiment(experiment)
    print 'Successfully added experiment (code={})'.format(info['code'])


def add_dummy_mobile_users(info):
    code, count = info['code'], info['count']
    for k in range(count):
        i = k + 1
        info = {
            'email': 'dummy{}{}@gmail.com'.format(str(i), code),
            'firstname': 'firstname{}'.format(str(i)),
            'lastname': 'lastname{}'.format(str(i)),
            'gender': 'male' if i % 2 == 0 else 'female',
            'condition': 1,
            'code': code
        }
        MobileUser.add_user(info)
    print 'Successfully added {} users (code={})'.format(count, code)


if __name__ == '__main__':
    main()
