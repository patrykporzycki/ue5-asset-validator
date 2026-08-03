#include "TexturePropsHelper.h"
#include "ImageUtils.h"
#include "ImageCore.h"


bool UTexturePropsHelper::ResizeTextureResolution(UTexture2D* Texture, int32 NewResolutionX, int32 NewResolutionY)
{
    if (!Texture) return false;

    FTextureSource& Source = Texture->Source;
    FImage SourceImage;
    if (!Source.GetMipImage(SourceImage, 0))
        return false;

    int32 OldResolutionX = Source.GetSizeX();
    int32 OldResolutionY = Source.GetSizeY();
    
    if (OldResolutionX == NewResolutionX && OldResolutionY == NewResolutionY)
        return false;

    FImageView DestImage;
    FImageCore::ResizeImageInPlace(SourceImage, NewResolutionX, NewResolutionY, SourceImage.Format, SourceImage.GetGammaSpace());
    
    Source.Init(NewResolutionX, NewResolutionY, 1, 1, Source.GetFormat(), SourceImage.RawData.GetData());

    
    Texture->UpdateResource();
    Texture->Modify();
    return true;
}