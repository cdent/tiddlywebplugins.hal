An effort to build a
[HAL](http://stateless.co/hal_specification.html) serializer for
TidldyWeb. The ideal outcomes of this experiment would be:

* A generic Python library for the JSON variant of HAL.
* Full navigation (hypermedia) of the core TiddlyWeb API.

Questions
=========

* It appears link rel can take object or list of objects. Does
  this cause pain?
* To what extent does it make sense to list _all_ the alternate
  representations of a resource.
* curie links...?
* What are the appropriate link rels for things like:
  * create a new bag
  * create a new recipe
  * create a new tiddler in this context (bag or recipe)
  
  Further how do we declare that the METHOD used is PUT and the
  media type is application/json? If that's what curie'd rels are
  for, to point to the docs, how's that better than just, say, 
  having some docs?
* It's clearly possible to make _many_ rels per entity, how to
  decide?
* Is HAL read-write or read (in general and in this application)

Plan
====

The plan is to first build the working TiddlyWeb solution and then
extract the generic parts. Effectively that means (in tests):

* open a GET to / Accept application/hal+json
* extract the content and validate
* extract the links and traverse


