#include "test_helpers.h"

bool version_patch_is_valid(int patch)
{
    return patch >= 0 && patch <= 999;
}
