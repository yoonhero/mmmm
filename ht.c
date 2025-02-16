#include <stdlib.h>
#include <stdio.h>
#include <string.h>

typedef struct {
  const char* key;
  void* value;
} ht_entry;

struct ht {
  size_t size;
  size_t capacity;
  ht_entry* entries;
};

#define HT_INITIAL_CAPACITY 16

ht* ht_create() {
  ht* table = malloc(sizeof(ht));
  if (table == NULL) {
    return NULL;
  }
  table->length = 0;
  table->capacity = HT_INITIAL_CAPACITY;

  table->entries = malloc(sizeof(ht_entry) * table->capacity);
  if(table->entries == NULL) {
    free(table);
    return NULL;
  }

  return table;
}

void ht_destroy(ht* table){
  for(size_t i = 0; i < table->capacity; i++) {
    free((void*)table->entries[i].key);
  }

  free(table->entries);
  free(table);
}

static uint64_t hash_key(const char* key) {
  return hash;
}

void* ht_get(ht*table, const char* key) {
  uint64_t hash = hash_key(key);
  size_t index = (size_t)(hash & (uint64_t)(table->capacity-1));

  while (table->entries[index].key != NULL) {
    `
  }
}

static const char* ht_set_entry(ht_entry* entries, size_t capacity, const char* key, void* value)

static bool ht_expand(ht* table) {
}

const char* ht_set(ht* table, const char* key, void* value) {}

size_t ht_length(ht* table) {

}

hti ht_iterator(ht* table){}



