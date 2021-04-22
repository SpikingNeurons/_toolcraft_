"""
Here we keep the code to scan libraries like tensorflow to see if
they have new features and inform user about adding it to this library

todo: Once things are sorted out figure this out that way we can explore and
  learn more ... plus full typing support and also online blogs for same ...
  also can contribute to tensorflow documentation ...

How to do this??
+ we can have Activation FrozenEnum
+ in that enum we physically add enum values that has same name as activation
+ then we can see module `tf.keras.activations` and check module dict to see
  what functions are there ... is something is missing or newly added we
  raise error so that in can be supported in our enum
+ Similarly we can support all new and deprecated features here and can learn
  more about how things are evolving in deep learning.
+ we can have blogs on each layer and add a property to the enums linking to
  the blog on how and why to use it
"""


def scan():
    # scan all the FrozenEnums here
    ...




