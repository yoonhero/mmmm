#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
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

typedef struct ArrayList {
  int *array;
  size_t length;
  size_t capacity;
} ArrayList;
// For generic type array => void *array+size_t elementSize / using (char *)array+elementSize for 1byte increment hack -> it's nice!

ArrayList createArrayList(size_t capacity){
  ArrayList list;
  list.array = (int *)malloc(capacity * sizeof(int));
  list.length = 0;
  list.capacity = capacity;
  return list;
}

void append(ArrayList *list, int value){
  if(list -> length == list -> capacity){
    list->capacity *= 2;
    //list->array = (int *)realloc(list->array, list->capacity * sizeof(int));
    int *new_array = (int *)malloc(list->capacity * sizeof(int));
 //   for(int i=0; i<list->length; i++){
 //     new_array[i] = list->array[i];
 //   }
    memcpy(new_array, list->array, list->length*sizeof(int));
    free(list->array);
    list->array = new_array;
    printf("Capacity increased to %zu\n", list->capacity);
  }

  list->array[list->length] = value;
  list->length++;
  return;
}

void* pop(ArrayList *list){
  if(list->length == 0){
    printf("Error; list is empty\n");
    return NULL;
  }

  //list->length--; // occasionally, it seems shirinking the capacity is also one way to optimize.
  // ++i->no copy, i++->copy(acts like js event listener)
  return &(list->array[--list->length]);
}

void removeItem(ArrayList *list, int index){
  if (index >= list->length){
    printf("Error: index out of range\n");
    return;
  }

// for(int i=index; i<list->length-1; i++){
 //   list->array[i] = list->array[i+1];
 // } // more effecient way? -> memmove? or memcpy?
  
  memmove(&list->array[index], &list->array[index+1], (list->length-index-1)*sizeof(int)); // safe-overlap vs overlapping(copy from the end of the blocks to the beginning, worrying about losing!)

  --list->length;
  return;
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

  // Array List(Dynamic sizing with data structures) - https://www.youtube.com/watch?v=xFMXIgvlgcY&t=169s
  // Linked list -> finding elements is fucking idiot! -> O(n) what a freaking slow!(cache hit)
  ArrayList list = createArrayList(2);
  append(&list, 1); // Dynamic sizing is making it has infinite size!
  append(&list, 2);
  append(&list, 3);
  int popped_val = *(int *)pop(&list);
  printf("poped %d!!\n", popped_val);
  removeItem(&list, 1); // Linked list is more efficient! -> just change the pointer directing to.
  printf("poped %d!!\n", *(int *)pop(&list));
  // Generic Type -> Why cache nightmare?(java, python->multiple type with array pointer, js->hash map!!!!)

  // Concurrecy - https://www.youtube.com/watch?v=3X93PnKRNUo 
    // Time-Sharing Operating System
      // Process(data structure) / Scheduler
      // CPU(fetch-jump/decode/execute) -> I/O(waiting on Queue) -> Dispatcher...
        // Infinite Loop without I/O waiting? -> Halting problem! ==> Preemptive Scheduling(Set Timer on it!)
    // Multi-core CPU (true parallelism)
    

  // Compiler = Memory Stack/Heap Manipulation Utilizer
    // AOT Optimization -> deep optim(inlining, vectorization...)
  // Interpreter = Read(Lexer), Parse(Parser), Execute
    // Lexer=Tokenizer / Parser=RPN(Shuting Yard Algorithm)->AST(Break&Conquer technique)
      // Parsing is a process of sorting human readable format to machine readable format (1+2*3 -> 1 2 3 * +)
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

  // CSs(Cascading Style Sheets X)
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
