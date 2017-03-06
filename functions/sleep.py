import time
def sleep():
	# > maximum timeout of Lambda
	time.sleep(310)
def lambda_handler(event, context):
	sleep()
