from clients import nova
import random
import time

def random_server_name():
    verbs = ('Burping','Farting','Throwing','Chucking','Kissing','Bumping','Joking', 'Running', 'Walking', 'Jumping', 'Bumping', 'Rolling')
    veggies = ('Alfalfa','Anise','Artichoke','Arugula','Asparagus','Aubergine','Azuki','Banana','Basil','Bean','Beet','Beetroot','bell','Black','Borlotti','Broad','Broccoflower','Broccoli','Brussels','Butternut','Cabbage','Calabrese','Capsicum','Caraway','Carrot','Carrots','Cauliflower','Cayenne','Celeriac','Celery','Chamomile','Chard','Chickpeas','Chili','Chives','Cilantro','Collard','Corn','Courgette','Cucumber','Daikon','Delicata','Dill','Eggplant','Endive','Fennel','Fiddleheads','Frisee','fungus','Garlic','Gem','Ginger','Grape','Habanero','Herbs','Horseradish','Hubbard','Jalapeno','Jicama','Kale','Kidney','Kohlrabi','Lavender','Leek','Legumes','Lemon','Lentils','Lettuce','Lima','Maize','Mangetout','Marjoram','Marrow','Mung','Mushrooms','Mustard','Nettles','Okra','Onion','Oregano','Paprika','Parsley','Parsley','Parsnip','Patty','Peas','Peppers','pimento','Pinto','plant','Potato','Pumpkin','Purple','Radicchio','Radish','Rhubarb','Root','Rosemary','Runner','Rutabaga','Rutabaga','Sage','Salsify','Scallion','Shallot','Skirret','Snap','Soy','Spaghetti','Spinach','Spring','Squash','Squashes','Swede','Sweet','Sweetcorn','Tabasco','Taro','Tat','Thyme','Tomato','Tubers','Turnip','Turnip','Wasabi','Water','Watercress','White','Yam','Zucchini','Lemon','Strawberry','Apple','Banana','Kiwi')
    name = '-'.join([random.choice(verbs), random.choice(veggies)])
    
    return name

def boot_server(hostname,ports):

    build_start = time.time()
    server = nova.servers.create(name=hostname,
                    image="f9cffd1e-b07f-42d0-9595-857bbd59cc26",
                    flavor="1",
                    nics=[{'port-id':ports['mgmt']}]
               )

    return server,build_start

def check_status(server_id):
    
    # Returns the status of the instance. Delayed (usually) by busy API.
    check_start = time.time()
#    print "DEBUG check status start: %s" % check_start
    server = nova.servers.get(server_id)
#    print "DEBUG check status duration: %s" % (time.time() - check_start)
    return server.status
