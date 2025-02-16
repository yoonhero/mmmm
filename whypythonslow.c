#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
// Preprocess # prefix - check hierarchy -> current workspace -> system 
// header file

struct Node {
  int data;
  struct Node *next;
}; // Byte padding -> 4+8 -> 16 bytes
// struct Node next -> error: make it infinite loop

// vs Union -> share the same memory space = not pre-defined the type of data(union Number int, long, ...?)

typedef struct Node Node; // override the name of existing type
// it seems `typedef struct {} Name` is a common pattern in C.

int searchDeepest(Node *cur){
  if(cur==NULL){
    printf("Error: linked list is empty\n");
    return -1;
  }

  if(cur->next == NULL){
    return cur->data;
  } else {
    return searchDeepest(cur->next);
  }
}
int main() {
  // What is variable type?
    // Size of variable metters - https://www.youtube.com/watch?v=hwyRnHA54lI
    // consume 1~8 bytes -> represent abstract meaning!
    // in low-level it probably gets into illegal memory handling (int + char)
    // prevent it with the Gatekeeper(Compiler)
    // We just make use of successive memory addresses and its value to build complex magics.
  int zero = 0;
  int one = 1;
  int *mem_zero = &zero;
  int *mem_one = &one;

  printf("%p, %p", mem_zero, mem_one);

  // Assuming current 64bit arch
  // Bit more about n-bit OS; (https://www.quora.com/Why-is-64-bit-faster-than-32)
    // Data Size & Address Size
    // 32-bit OS's RAM Capacity < 4GB by inherent limitation! (that's big deal)
      // complex approaches (context switching in OS) -> 64bit is less efficient but conveninent!
    // 32 program -> 64 OK; 64 -> 32 not OK;
    // Enhanced instruction set, Improved Perf for multithreading, Reduced memory overhead(less call?)
  int diff = (int64_t)(mem_one) - (int64_t)(mem_zero);

  printf("diff = %d\n", diff);
  // size of int is 4 bytes stack grows upwards -> -4
  if(diff==-4){
    printf("Memory is contiguous\n");
  }
  // https://www.quora.com/How-is-struct-in-C-languages-built-Does-it-have-a-continuous-address-space-in-RAM
  // Big endian(MSB->LSB, in common cpus) vs Small endian(in intel cpus) -> may get reverse result
  uint32_t num = 0x12345678;
  uint8_t high_byte = (num >> 24) & 0xFF; // MSB
  uint8_t low_byte = num & 0xFF; // LSB
  char *p = (char *)&num;
  for (int i=0; i<sizeof(num); i++){
    printf("%x", p[i]);
  } // let me know whether your system is big or small endian.

  // Memory Layout
    // STACK - https://www.youtube.com/watch?v=N3o5yHYLviQ
      // maximize the chance of cache hit! -> LIFO(Last in first out)
      // variable scope -> stack area!
    // HEAP - https://www.youtube.com/watch?v=ioJkA7Mw2-U
      // Dynamic expanding(syscall -> why it slow!)
      // memory fragmentation(best fit, worst fit, first fit...) -> anywhere can be "free"
        // malloc, free
      // Dynamic List - linked list, array list
  int array[3] = {1, 2, 3};
  size_t size = sizeof(array)/sizeof(int);
  int *end_ptr = array+size;
  for(int i = 0; i<size; i++){
    printf("Address: %p", &array[i]);
    printf("Value: %d", array[i]);
    printf("Is same: %d\n", array[i] == *(array+i));
  }
  for(int *ptr = array; ptr<end_ptr; ptr++){
    printf("%d\n", *ptr);
  }  

  int *array_ptr = array; // pointer to first element
  int (*array_ptr_)[3] = &array; // pointer to array of 5 elements

  printf("Array ptr test\n");
  while (array_ptr < array+size){
    printf("%d\n", (int)*array_ptr);
    array_ptr++; // why pointer is not int, but int* (normal increment is not utilizable) - https://www.quora.com/Why-cant-we-store-addresses-in-normal-int-variables-Why-the-separate-*-notation-for-pointers
  }

  // How to be a dynamic?
  // Linked List -> May be non-contiguous, but it's okay!
  Node head;
  Node current;

  head.next = &current;
  current.data = 1;
  current.next = NULL;
  printf("%d\n", head.next->data);
  
  int data = searchDeepest(&head);
  printf("%d\n", data);

  struct Node *head_ = (Node *)malloc(sizeof(Node));
  struct Node *current_ = (Node *)malloc(sizeof(Node));

  if (head_ == NULL || current_ == NULL){
    printf("Error: Memory allocation failed\n");
    return -1;
  }

  head_->data = 10;
  head_->next = current_;
  current_->data = 30;
  current_->next = NULL;

  data = searchDeepest(head_);
  printf("%d\n", data);

  free(head_);
  free(current_);

  // Arraylist
  

  // Compiler = Memory Stack/Heap Manipulation Utilizer
    // AOT Optimization -> deep optim(inlining, vectorization...)
  // Interpreter = Read(Lexer), Parse(Parser), Execute
    // Lexer=Tokenizer / Parser=RTN(Shuting Yard Algorithm)->AST(Break&Conquer technique)
      // Parsing is a process of sorting human readable to machine readable format (1+2*3 -> 1 2 3 * +)
      // Function state space, variable scope, args function calling.. -> more complex things! (but it's not big deal)
    // JIT(Just in time) execution = parse+execute all in onece!
    // Execution = Where the overhead comes from!
      // Lexing, Parsing - Once
      // Dynamic type checks(stop complex operation party!), dynamic dispatch, and the per-instructino interpreter loop -> Gangstar!
        // Computer on computer(AST = memory map) -> slow!
        // Reducing fetching, decoding, and dispatching overheads -----> Real Problem!
          // Why fucking slow loop? -> fure call overhead xN
            // JIT compiler observing low-entropy code call dup - Bytecode(Intermediate level) -> Machine code
          // GC -> no need to make fussy keep concise.
      // **solution** I think might effective -> Compress AST Block-by-Block! to reduce call?(cache-hit) = JIT Apro? slightly different in some manner.
  // Run time <<<<< Developer time (in most case)

  // CSs(Cascading Syle Sheets X)
  // hash table
    // Maximize the hashing function ability to make O(1)!
      // hash(key) mod N -> index
      // hash collision -> chaining (linked list)
        // offensive attack can occur in this point(if hacker knows the hash function -> make it O(n))
      // further improvs -> Hash table Expand(x2)+ ...
    // Good Works! - https://benhoyt.com/writings/hash-table-in-c/
    // How python builds in disctionaries implemented? - https://stackoverflow.com/questions/327311/how-are-pythons-built-in-dictionaries-implemented/44509302#44509302
      // shared keys, multiple hash functions(lack of FNV, reverse hasing...), ... (more on PEP maybe?)
        // __slot__ -> optimize class instance! (not doing so much on basic components)
        // class instance = __dict__ (use when you have no idea with foreign class)
  // FS(File System)
    // FAT
      // Problems: finite number of addressable storage blocks+store varying sizes
      // store value in small, addressable chunks! -> linked list to expand its volume
        // non-contiguous or poor random access perf
      // Direcotries = special files whose contents are structured lists of file metadata
    // Inode -> direct pointers
  // Buffer(gate -> flush! for desired action)
  // 2-Compliment -> overflow = no other +-0
  return 0;
} 
