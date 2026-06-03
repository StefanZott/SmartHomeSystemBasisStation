#include "unity.h"
#include "test_helpers.h"

TEST_CASE("version patch accepts valid range", "[smoke]")
{
    TEST_ASSERT_TRUE(version_patch_is_valid(0));
    TEST_ASSERT_TRUE(version_patch_is_valid(1));
    TEST_ASSERT_TRUE(version_patch_is_valid(999));
}

TEST_CASE("version patch rejects out of range", "[smoke]")
{
    TEST_ASSERT_FALSE(version_patch_is_valid(-1));
    TEST_ASSERT_FALSE(version_patch_is_valid(1000));
}

TEST_CASE("unity smoke", "[smoke]")
{
    TEST_ASSERT_EQUAL(1, 1);
}

void app_main(void)
{
    unity_run_all_tests();
}
