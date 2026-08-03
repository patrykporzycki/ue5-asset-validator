#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "TexturePropsHelper.generated.h"

UCLASS()
class ASSETVALIDATOREDITOR_API UTexturePropsHelper : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "Asset Validator|Texture 2D Props")
	static bool ResizeTextureResolution(UTexture2D* Texture, int32 NewResolutionX, int32 NewResolutionY);
};