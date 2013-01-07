
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

Plan
====

The plan is to first build the working TiddlyWeb solution and then
extract the generic parts. Effectively that means (in tests):

* open a GET to / Accept application/hal+json
* extract the content and validate
* extract the links and traverse


