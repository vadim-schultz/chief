#include <cassert>
#include <string>

#include "greeting.h"

int main() {
  assert(greet("Ada") == "Hello, Ada!");
  return 0;
}
