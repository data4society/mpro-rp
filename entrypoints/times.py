"""get procedures times and write them"""
import sys
sys.path.insert(0, '..')
import os


if __name__ == '__main__':
    print("START TIMING")
    print(os.environ['TRAVIS_COMMIT_RANGE'])
    print(os.environ['MY_PASSWORD'])
    print(type(os.environ['TRAVIS_COMMIT_RANGE']))
    #print(type(sys.argv[1]))
    #delete_document('f83eaba6-be71-4472-81f0-f57b8838461b')
    #delete_app_documents('read_test')
    print("FINISH TIMING")