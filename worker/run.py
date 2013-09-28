#!/usr/bin/env python

import os
import sys
import time
import logging
from queue import queue_daemon

root_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(root_path, 'lib'))
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
        level=logging.INFO)
logger = logging.getLogger('worker')


def load_modules(path, prefix):
    for fname in os.listdir(os.path.join(root_path, path)):
        if not fname.startswith(prefix) or not fname.endswith('.py'):
            continue
        name = fname[:-3]
        try:
            mod = __import__('{0}.{1}'.format(path, name), globals(),
                    locals(), [name], -1)
            yield mod
        except Exception as e:
            logger.warning('Ignoring "{0}": {1}'.format(name, e))


def run_module(mod, *args):
    logger.info('{0}: started'.format(mod.__name__))
    if not hasattr(mod, 'run'):
        logger.warning('{0} has no entry point.'.format(mod.__name__))
        return
    retry = 3
    result = None
    while retry > 0:
        try:
            mod.logger = logger
            result = mod.run(*args)
            break
        except Exception as e:
            logger.exception('{0}: returned an error.'
                    ' Retrying in 1 second...'.format(mod.__name__))
            retry -= 1
            time.sleep(1)
            continue
    return result


def process_result(mod, project, result):
    """ given a result dictionary process it """
    result['timestamp'] = int(time.time())
    logger.info('{0}: finished'.format(mod.__name__))
    for hook in load_modules('hooks', 'hook'):
        run_module(hook, project, result.copy())


def run_analytics(project):
    full_results = []
    for mod in load_modules('attributes', 'attrib'):
        result = run_module(mod, project)
        if not result:
            logger.error('{0}: did not return any result'.format(mod.__name__))
            continue
        if isinstance(result, list):
            # if the module returned a list, process one at a time.
            for res in result:
                full_results.append(res)
                process_result(mod, project, res)
        else:
            # it was a dict result process like normal.
            full_results.append(result)
            process_result(mod, project, result)
    return full_results


def clone_project(project):
    """ Clone the project locally """
    # todo actually do the clone
    project_directory = "/tmp"
    return project_directory


def pre_job(project):
    """ run before it gets started. alter project input if needed"""
    project_directory = clone_project(project)
    project['project_directory'] = project_directory
    return project


def post_job(project, post_results):
    """ runs after the project is finished processing"""
    pass


def handle_job(project):
    logger.info('Starting... {0}'.format(project))
    project = pre_job(project)
    results = run_analytics(project)
    post_job(project, post_results)
    logger.info('Finsihed... {0}'.format(project))


def run():
    #TODO: add multi workers to speed things up.
    try:
        queue_daemon(handle_job)
    except Exception as e:
        logger.error(e)


if __name__ == '__main__':
    logger.info('Starting worker')
    run()